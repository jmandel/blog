// Browser session, pacing, safe clicking and the in-page extractors.
// Selectors come from ./selectors.ts; nothing here should name a LinkedIn
// class directly.

import puppeteer from "puppeteer-core";
import type { Browser, Page, ElementHandle, HTTPResponse } from "puppeteer-core";
import { SEL, TEXT } from "./selectors.ts";

export class Blocked extends Error {}
export class BudgetExceeded extends Error {}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const jitter = (lo: number, hi: number) => lo + Math.random() * (hi - lo);

export interface SessionOptions {
  cdpUrl: string;
  maxPages: number;
  minDelayMs: number;
  maxDelayMs: number;
  log: (rec: Record<string, unknown>) => void;
}

// One tab of our own in the user's logged-in browser. All navigation goes
// through goto(), which paces loads and counts them against --max-pages.
export class Session {
  opts: SessionOptions;
  browser!: Browser;
  page!: Page;
  pageLoads = 0;
  clicks = 0;
  lastLoad = 0;
  // Bodies of media responses the page loaded itself, by URL, so images
  // shown on the page are saved without a second request.
  mediaCache = new Map<string, { type: string; body: Buffer }>();

  constructor(opts: SessionOptions) {
    this.opts = opts;
  }

  async open(): Promise<void> {
    this.browser = await puppeteer.connect({ browserURL: this.opts.cdpUrl, defaultViewport: null });
    this.page = await this.browser.newPage();
    this.page.setDefaultTimeout(20000);
    this.page.on("response", (r: HTTPResponse) => this.onResponse(r));
  }

  async close(): Promise<void> {
    try { await this.page?.close(); } catch { /* already closed */ }
    try { this.browser?.disconnect(); } catch { /* ignore */ }
  }

  private async onResponse(r: HTTPResponse): Promise<void> {
    const url = r.url();
    if (!/^https:\/\/(media|dms)\.licdn\.com\//.test(url)) return;
    if (/profile-(display|framed|original)photo|company-logo|displaybackgroundimage|static\.licdn/.test(url)) return;
    if (/iso\.segment|dash\+xml/.test(r.headers()["content-type"] || "")) return;
    if (r.status() !== 200) return;
    try {
      const body = await r.buffer();
      if (body.length > 25e6) return;
      this.mediaCache.set(url, { type: r.headers()["content-type"] || "", body });
      if (this.mediaCache.size > 400) this.mediaCache.delete(this.mediaCache.keys().next().value!);
    } catch { /* body evicted; downloadMedia falls back to a fetch */ }
  }

  async pace(): Promise<void> {
    const wait = this.lastLoad + jitter(this.opts.minDelayMs, this.opts.maxDelayMs) - Date.now();
    if (wait > 0) await sleep(wait);
  }

  async goto(url: string, kind: string): Promise<void> {
    if (this.pageLoads >= this.opts.maxPages) throw new BudgetExceeded(`page budget of ${this.opts.maxPages} reached before ${url}`);
    await this.pace();
    this.pageLoads++;
    this.lastLoad = Date.now();
    this.opts.log({ ev: "load", n: this.pageLoads, kind, url });
    await this.page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
    await sleep(jitter(2500, 4000));
    await this.checkBlocked();
    await this.installHelpers();
  }

  async checkBlocked(): Promise<void> {
    const url = this.page.url();
    const title = await this.page.title().catch(() => "");
    const dom = await this.page.evaluate((sels: string[]) => sels.some((s) => document.querySelector(s)), SEL.blockedDom).catch(() => false);
    if (SEL.blockedUrl.some((re) => re.test(new URL(url).pathname)) || SEL.blockedTitle.some((re) => re.test(title)) || dom) {
      throw new Blocked(`LinkedIn is asking for a login or a check (${new URL(url).pathname}, "${title}"). Stopped; do not try to get past it.`);
    }
  }

  // Scroll down in small human-sized steps until `done()` or the step cap.
  // Scrolls the window, or the element that actually scrolls: the
  // server-driven layout scrolls an inner container (the document is only
  // one screen tall).
  async scrollGradually(steps: number, done?: () => Promise<boolean>): Promise<number> {
    let i = 0;
    for (; i < steps; i++) {
      if (done && (await done())) break;
      await this.page.evaluate(scrollStep, Math.round(jitter(500, 900)));
      await sleep(jitter(700, 1400));
    }
    return i;
  }

  // { atBottom, height } of whatever scrolls (window or inner container).
  async scrollState(): Promise<{ atBottom: boolean; height: number }> {
    return this.page.evaluate(() => {
      const el = (window as any).__lfScroller?.() as Element | null;
      if (!el) return { atBottom: window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 300, height: document.documentElement.scrollHeight };
      return { atBottom: el.scrollTop + el.clientHeight >= el.scrollHeight - 300, height: el.scrollHeight };
    });
  }

  // Click only whitelisted expanders (selectors.ts → SEL.expanders), after
  // re-checking the element's label against the never-click patterns.
  async safeClick(el: ElementHandle<Element>, kind: keyof typeof SEL.expanders): Promise<boolean> {
    const spec = SEL.expanders[kind];
    const info = await el.evaluate((e: Element, sels: string[]) => {
      const text = ((e as HTMLElement).innerText || "").trim();
      const aria = e.getAttribute("aria-label") || "";
      return { text, aria, ok: sels.some((s) => e.matches(s)), visible: !!(e as HTMLElement).offsetParent };
    }, spec.sel);
    if (!info.ok || !info.visible || !(spec.label.test(info.text) || spec.label.test(info.aria))) return false;
    if (SEL.neverClickText.test(info.text) || SEL.neverClickAria.test(info.aria)) {
      this.opts.log({ ev: "refused-click", kind, text: info.text, aria: info.aria });
      return false;
    }
    await el.evaluate((e: Element) => e.scrollIntoView({ block: "center" }));
    await sleep(jitter(500, 1100));
    try {
      await el.click();
    } catch {
      await el.evaluate((e: Element) => (e as HTMLElement).click());
    }
    this.clicks++;
    await sleep(jitter(800, 1600));
    return true;
  }

  async installHelpers(): Promise<void> {
    const sel = JSON.parse(JSON.stringify(SEL));
    sel.expanderSkipSource = SEL.expanderSkip.source;
    for (const [k, v] of Object.entries(SEL.expanders)) sel.expanders[k].labelSource = v.label.source;
    await this.page.evaluate(installHelpers, sel, {
      relativeTime: TEXT.relativeTime.source, editedMarker: TEXT.editedMarker.source, authorBadge: TEXT.authorBadge.source,
      commentsCount: TEXT.commentsCount.source, repostsCount: TEXT.repostsCount.source, repliesCount: TEXT.repliesCount.source,
      repostHeader: TEXT.repostHeader.source,
    });
  }

  // Fetch a media file: from the page's own responses if it loaded it,
  // else with the page's fetch (cookies apply), else from Node (LinkedIn's
  // media URLs are signed, so most work without cookies). Each source must
  // return a plausible file (media content type, ≥ 200 bytes).
  async downloadMedia(url: string): Promise<{ type: string; body: Buffer; via: string } | { error: string }> {
    const ok = (t: string, b: Buffer) => b.length >= 200 && /^(image|video|audio|text\/vtt|application\/(pdf|octet-stream))/.test(t);
    const tried: string[] = [];
    const hit = this.mediaCache.get(url);
    if (hit && ok(hit.type, hit.body)) return { ...hit, via: "page response" };
    tried.push(hit ? `cache: ${hit.type} ${hit.body.length}B` : "cache: miss");
    const inPage = await this.page.evaluate(async (u: string) => {
      try {
        const r = await fetch(u, { credentials: "include" });
        if (!r.ok) return { err: `HTTP ${r.status}` };
        const buf = new Uint8Array(await r.arrayBuffer());
        let s = "";
        for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode(...buf.subarray(i, i + 0x8000));
        return { type: r.headers.get("content-type") || "", b64: btoa(s) };
      } catch (e) { return { err: String(e).slice(0, 80) }; }
    }, url).catch((e: Error) => ({ err: e.message.slice(0, 80) }));
    if ("b64" in inPage && inPage.b64 != null) {
      const body = Buffer.from(inPage.b64, "base64");
      if (ok(inPage.type!, body)) return { type: inPage.type!, body, via: "page fetch" };
      tried.push(`page fetch: ${inPage.type} ${body.length}B`);
    } else tried.push(`page fetch: ${(inPage as any).err}`);
    try {
      const r = await fetch(url, { headers: { "user-agent": "Mozilla/5.0" } });
      const body = Buffer.from(await r.arrayBuffer());
      const type = r.headers.get("content-type") || "";
      if (r.ok && ok(type, body)) return { type, body, via: "direct" };
      tried.push(`direct: HTTP ${r.status} ${type} ${body.length}B`);
    } catch (e) { tried.push(`direct: ${String(e).slice(0, 80)}`); }
    return { error: tried.join("; ") };
  }
}

// Runs in the page: scroll the window if the document is taller than the
// viewport, else the largest scrollable element.
function scrollStep(dy: number) {
  const w = window as any;
  w.__lfScroller = () => {
    if (document.documentElement.scrollHeight > window.innerHeight + 50) return null;
    let best: Element | null = null, room = 0;
    for (const e of document.querySelectorAll("main, div, section")) {
      const r = e.scrollHeight - e.clientHeight;
      if (r > room && /(auto|scroll)/.test(getComputedStyle(e).overflowY)) { best = e; room = r; }
    }
    return best;
  };
  const el = w.__lfScroller();
  if (el) el.scrollBy(0, dy); else window.scrollBy(0, dy);
}

// ---------------------------------------------------------------------------
// In-page helpers. Installed into each page as window.__lf; they only read
// the DOM. Must be self-contained (they run in the browser).
// ---------------------------------------------------------------------------
function installHelpers(S: any, R: Record<string, string>) {
  const re = (k: string, f = "i") => new RegExp(R[k], f);
  const missed: string[] = [];
  const q = (root: ParentNode, key: string): Element | null => {
    const list: string[] = S[key];
    for (const s of list) { try { const e = root.querySelector(s); if (e) return e; } catch { /* bad selector */ } }
    return null;
  };
  const qa = (root: ParentNode, key: string): Element[] => {
    const list: string[] = S[key];
    for (const s of list) { try { const e = [...root.querySelectorAll(s)]; if (e.length) return e; } catch { /* bad selector */ } }
    return [];
  };
  const txt = (e: Element | null) => (e ? ((e as HTMLElement).innerText || e.textContent || "").replace(/\s+/g, " ").trim() : "");
  const num = (s: string | undefined | null) => { if (!s) return null; const m = s.replace(/,/g, "").match(/(\d+(?:\.\d+)?)\s*([KkMm])?/); if (!m) return null; let n = parseFloat(m[1]); if (m[2]) n *= /k/i.test(m[2]) ? 1e3 : 1e6; return Math.round(n); };
  const abs = (href: string) => { try { return new URL(href, location.origin).href; } catch { return href; } };
  const unwrap = (href: string) => {
    let u = abs(href);
    for (let i = 0; i < 3; i++) {
      try {
        const p = new URL(u);
        if (/linkedin\.com$/.test(p.hostname) && /^\/(redir|safety\/go)\//.test(p.pathname) && p.searchParams.get("url")) { u = p.searchParams.get("url")!; continue; }
        if (/linkedin\.com$/.test(p.hostname) && /^\/(in|company|school)\//.test(p.pathname)) { p.search = ""; u = p.href; }
        else { for (const k of [...p.searchParams.keys()]) if (/^(trk|trackingId|utm_|lipi|midToken|midSig|miniProfileUrn)/.test(k)) p.searchParams.delete(k); u = p.href; }
      } catch { /* leave as is */ }
      break;
    }
    return u;
  };
  const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  // Text, minimal HTML (<a>, <br>), links, @-mentions and hashtags of a
  // LinkedIn rich-text block. Uses textContent, so text hidden behind
  // "…more" (already in the DOM, clamped by CSS) is included.
  const rich = (root: Element | null) => {
    const out = { text: "", html: "", links: [] as any[], mentions: [] as any[], hashtags: [] as string[] };
    if (!root) return out;
    const walk = (n: Node) => {
      if (n.nodeType === 3) { const t = n.textContent || ""; out.text += t; out.html += esc(t); return; }
      if (n.nodeType !== 1) return;
      const e = n as HTMLElement;
      if (e.matches("button, .visually-hidden, svg, script, style, img")) return;
      if (e.tagName === "BR") { out.text += "\n"; out.html += "<br>"; return; }
      if (e.classList.contains("white-space-pre")) { out.text += " "; out.html += " "; return; }
      if (e.tagName === "A") {
        const href = unwrap(e.getAttribute("href") || "");
        const vis = e.cloneNode(true) as HTMLElement;
        vis.querySelectorAll(".visually-hidden").forEach((h) => h.remove());
        const label = (vis.textContent || "").replace(/\s+/g, " ").trim();
        if (/linkedin\.com\/(in|company|school)\//.test(href)) out.mentions.push({ name: label, url: href, kind: /\/in\//.test(href) ? "person" : "organization" });
        else if (/keywords=%23|\/feed\/hashtag\//.test(href)) out.hashtags.push(label.replace(/^#/, ""));
        else out.links.push({ text: label, url: href });
        out.text += label;
        out.html += `<a href="${esc(href)}">${esc(label)}</a>`;
        return;
      }
      const block = /^(P|DIV|LI|H\d)$/.test(e.tagName) && out.text && !out.text.endsWith("\n");
      if (block) { out.text += "\n"; out.html += "<br>"; }
      e.childNodes.forEach(walk);
    };
    walk(root);
    out.text = out.text.replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
    out.html = out.html.replace(/^(\s|<br>)+|(\s|<br>)+$/g, "");
    return out;
  };

  const counts = (root: ParentNode) => {
    const box = q(root, "socialCounts");
    const t = txt(box);
    return {
      reactions: num(txt(box ? q(box, "reactionsCount") : null)),
      comments: num((t.match(re("commentsCount")) || [])[1]) ?? (box ? 0 : null),
      reposts: num((t.match(re("repostsCount")) || [])[1]) ?? (box ? 0 : null),
      raw: t,
    };
  };

  const mediaImgs = (root: Element) => [...root.querySelectorAll("img")]
    .map((i) => ({ src: (i as HTMLImageElement).currentSrc || (i as HTMLImageElement).src, alt: i.getAttribute("alt") || "" }))
    .filter((i) => /^https:\/\/media\.licdn\.com\//.test(i.src) && !/profile-(display|framed)photo|company-logo|reactions-icon|static\.licdn/.test(i.src));

  const comment = (a: Element, me: string) => {
    const id = a.getAttribute("data-id") || "";
    const parentEl = a.parentElement?.closest("article.comments-comment-entity");
    const authorA = q(a, "commentAuthorLink") as HTMLAnchorElement | null;
    const metaContainer = a.querySelector(":scope > div") || a;
    const own = (sel: string) => { const e = q(a, sel); return e && e.closest("article.comments-comment-entity") === a ? e : null; };
    const textEl = own("commentText");
    const content = own("commentContent");
    const profile = authorA ? unwrap(authorA.getAttribute("href") || "") : "";
    const metaText = txt(metaContainer.querySelector(".comments-comment-meta__container") || metaContainer);
    const media: any[] = [];
    if (content) {
      for (const img of mediaImgs(content)) media.push({ type: /\.gif|giphy|gif-/i.test(img.src) ? "gif" : "image", url: img.src, alt: img.alt });
      for (const card of content.querySelectorAll("article, .comments-comment-item__card, [class*='article-card']")) {
        const link = card.querySelector("a[href]");
        if (link) media.push({ type: "link_preview", url: unwrap(link.getAttribute("href")!), title: txt(card).slice(0, 300) });
      }
    }
    const reactionsEl = own("commentReactions");
    const replyCountEl = own("commentReplyCount");
    const timeEl = own("commentTime");
    return {
      id,
      parent_id: parentEl ? parentEl.getAttribute("data-id") : null,
      is_reply: a.classList.contains(S.commentIsReply),
      author: {
        name: txt(own("commentAuthorName")),
        headline: txt(own("commentAuthorHeadline")),
        profile_url: profile,
        is_self: !!me && profile.replace(/\/$/, "").toLowerCase().endsWith(me.toLowerCase()),
        is_post_author: re("authorBadge", "").test(metaText),
      },
      time_text: txt(timeEl),
      edited: re("editedMarker", "").test(metaText) || /\(edited\)/i.test(txt(a.querySelector(".comments-comment-meta__info"))),
      ...(() => { const r = rich(textEl); return { text: r.text, html: r.html, links: r.links, mentions: r.mentions, hashtags: r.hashtags }; })(),
      media,
      reactions: num(txt(reactionsEl)) ?? 0,
      replies_displayed: num((txt(replyCountEl).match(re("repliesCount")) || [])[1]),
      missing: [!id && "id", !txt(own("commentAuthorName")) && "author", !txt(timeEl) && "time", !textEl && !media.length && "text"].filter(Boolean),
    };
  };

  const post = (card: Element) => {
    const quoted = q(card, "quotedWrapper");
    const inQuoted = (e: Element | null) => !!(quoted && e && quoted.contains(e));
    const own = (key: string) => qa(card, key).find((e) => !inQuoted(e)) || null;
    const header = q(card, "repostHeader");
    const isRepost = !!header && re("repostHeader").test(txt(header));
    const actorA = own("actorLink") as HTMLAnchorElement | null;
    const timeText = txt(own("actorTime"));
    const textEl = own("postText");
    const r = rich(textEl);
    const media: any[] = [];
    const found = new Set<string>();
    const imgs = qa(card, "images").filter((e) => !inQuoted(e));
    imgs.forEach((i, idx) => media.push({ type: "image", index: idx, url: (i as HTMLImageElement).currentSrc || (i as HTMLImageElement).src, alt: i.getAttribute("alt") || "" }));
    if (imgs.length) found.add("image");
    for (const v of qa(card, "video").filter((e) => !inQuoted(e))) {
      const vid = v as HTMLVideoElement;
      const tracks = [...vid.querySelectorAll("track")].map((t) => (t as HTMLTrackElement).src).filter(Boolean);
      media.push({ type: "video", poster: vid.poster || "", duration_s: isFinite(vid.duration) ? Math.round(vid.duration) : null, src: /^blob:/.test(vid.src) ? null : vid.src || null, captions: tracks });
      found.add("video");
    }
    for (const art of qa(card, "externalArticle").filter((e) => !inQuoted(e))) {
      const link = q(art, "externalArticleLink") as HTMLAnchorElement | null;
      const img = mediaImgs(art)[0];
      media.push({ type: "link_preview", url: link ? unwrap(link.getAttribute("href") || "") : "", title: txt(q(art, "externalArticleTitle")), subtitle: txt(q(art, "externalArticleSubtitle")), image: img ? img.src : null });
      found.add("link_preview");
    }
    for (const art of qa(card, "firstPartyArticle").filter((e) => !inQuoted(e))) {
      const link = art.querySelector("a[href*='/pulse/']") as HTMLAnchorElement | null;
      const img = mediaImgs(art)[0];
      media.push({ type: "article", url: link ? unwrap(link.getAttribute("href") || "").split("?")[0] : "", title: txt(art.querySelector("h2, .update-components-article-first-party__title, [class*='title']")) || "", image: img ? img.src : null });
      found.add("article");
    }
    for (const d of qa(card, "document").filter((e) => !inQuoted(e))) {
      const ifr = q(d, "documentIframe") as HTMLIFrameElement | null;
      media.push({ type: "document", title: txt(d).slice(0, 200), iframe: ifr ? ifr.src : null, pages: mediaImgs(d).map((i) => i.src), download: (d.querySelector("a[download], a[href*='.pdf']") as HTMLAnchorElement | null)?.href || null });
      found.add("document");
    }
    for (const p of qa(card, "poll").filter((e) => !inQuoted(e))) {
      const opts = qa(p, "pollOption").map((o) => txt(o));
      media.push({ type: "poll", question: txt(p.querySelector("h2, h3, [class*='question']")), options: opts, raw: txt(p).slice(0, 500) });
      found.add("poll");
    }
    // Components nobody has written an extractor for yet: report them.
    const known = /^update-components-(actor|text|header|image|linkedin-video|article|article-first-party|document|poll|mini-update-v2|update-v2|celebration|entity)$/;
    const unknown = [...new Set([...card.querySelectorAll("[class*='update-components-']")].flatMap((e) => [...e.classList]).filter((c) => /^update-components-[a-z-]+$/.test(c) && !c.includes("--")).map((c) => c))].filter((c) => !known.test(c));
    let quote: any = null;
    if (quoted) {
      const ql = q(quoted, "quotedLink") as HTMLAnchorElement | null;
      const qa_ = q(quoted, "actorLink") as HTMLAnchorElement | null;
      const qr = rich(q(quoted, "postText"));
      quote = { activity_urn: ((ql?.getAttribute("href") || "").match(/urn:li:activity:\d+/) || [null])[0], author: { name: txt(q(quoted, "actorName")), profile_url: qa_ ? unwrap(qa_.getAttribute("href") || "") : "" }, text: qr.text, images: mediaImgs(quoted).filter((i) => /feedshare/.test(i.src)).map((i) => i.src) };
    }
    return {
      activity_urn: card.getAttribute("data-urn"),
      kind: isRepost ? "repost" : quoted ? "quote" : "original",
      author: { name: txt(own("actorName")), headline: txt(own("actorHeadline")), profile_url: actorA ? unwrap(actorA.getAttribute("href") || "") : "" },
      time_text: timeText,
      edited: re("editedMarker", "").test(timeText),
      text: r.text, html: r.html, links: r.links, mentions: r.mentions, hashtags: r.hashtags,
      media, media_types: [...found], unknown_components: unknown, quote,
      counts: counts(card),
      missing: [!actorA && "actor", !textEl && !media.length && "text", !timeText && "time"].filter(Boolean),
    };
  };

  // --- server-driven layout (selectors.ts → SEL.sdui) ---------------------
  const sq = (root: ParentNode, key: string) => { for (const sel of S.sdui[key]) { const e = root.querySelector(sel); if (e) return e; } return null; };
  const sqa = (root: ParentNode, key: string) => { for (const sel of S.sdui[key]) { const e = [...root.querySelectorAll(sel)]; if (e.length) return e; } return [] as Element[]; };
  // "EgsIgIC68IjqsMPQAQ-replaceableCommentTools…" → urn:li:ugcPost:<id>
  const keyUrn = (key: string) => {
    try {
      const b = Uint8Array.from(atob(key.split("-replaceableCommentTools")[0].replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));
      const type = b[0] === 0x0a ? "activity" : b[0] === 0x12 ? "ugcPost" : null;
      if (!type || b[2] !== 0x08) return null;
      let v = 0n, shift = 0n;
      for (let i = 3; i < b.length; i++) { v |= BigInt(b[i] & 0x7f) << shift; shift += 7n; if (!(b[i] & 0x80)) break; }
      return `urn:li:${type}:${v >> 1n}`;
    } catch { return null; }
  };
  const bestSrc = (img: HTMLImageElement) => {
    const set = (img.getAttribute("srcset") || "").split(",").map((x) => x.trim().split(/\s+/)).filter((x) => x[0]);
    const scored = set.map(([u, w]) => [u, /high-res/.test(u) ? 1e9 : parseInt(w) || 0] as [string, number]).sort((a, b) => b[1] - a[1]);
    return scored[0]?.[0] || img.currentSrc || img.src;
  };
  const relTime = /^\d+\s?(s|m|h|d|w|mo|y|yr)\b/;
  const sduiPost = (card: Element) => {
    const toolsEl = sq(card, "commentToolsKey");
    const postUrn = toolsEl ? keyUrn(toolsEl.getAttribute("componentkey") || "") : null;
    const actLink = sq(card, "activityLink") as HTMLAnchorElement | null;
    const activity = actLink ? (actLink.href.match(/urn:li:activity:\d+/) || [null])[0] : null;
    const isRepost = [...card.querySelectorAll("p")].slice(0, 3).some((p) => re("repostHeader").test(txt(p)));
    const actors = sqa(card, "actorBlock").filter((e) => txt(e));
    const qLink = (sqa(card, "quotedLink") as HTMLAnchorElement[]).find((a) => !/urn:li:activity:/.test(a.href) || a.href.includes("feed/update"));
    // Quoted post: the smallest element holding the second author block and
    // the link to the quoted post.
    let quoted: Element | null = null;
    if (qLink && actors.length > 1) { quoted = actors[1]; while (quoted && !quoted.contains(qLink)) quoted = quoted.parentElement; }
    const inQ = (e: Element | null) => !!(quoted && e && quoted.contains(e));
    const actor = actors[0] || null;
    const actorA = actor?.closest("a") as HTMLAnchorElement | null;
    const timeEl = [...card.querySelectorAll("p, span")].find((e) => !inQ(e) && relTime.test(txt(e)) && e.children.length <= 1 && txt(e).length < 30) || null;
    let box: Element | null = actor; while (box && timeEl && !box.contains(timeEl)) box = box.parentElement;
    const firstText = (e: Element | null): string => (e ? [...e.querySelectorAll("span, p")].map((x) => txt(x)).find(Boolean) || "" : "");
    const name = firstText(actor);
    const headline = box ? ([...box.querySelectorAll("p")].map((p) => txt(p)).find((t) => t && t !== name && !t.startsWith("•") && !relTime.test(t) && !/visit my website|reposted this/i.test(t) && !t.startsWith(name)) || "") : "";
    const textEl = sqa(card, "text").find((e) => !inQ(e)) || null;
    const r = rich(textEl);
    const media: any[] = [];
    const found = new Set<string>();
    const seenImg = new Set<Element>();
    for (const a of sqa(card, "articleCard").filter((e) => !inQ(e))) {
      const img = a.querySelector("img") as HTMLImageElement | null;
      if (img) seenImg.add(img);
      const url = unwrap(a.getAttribute("href")!).split("?")[0].replace(/\/$/, "");
      const prev = media.find((m) => m.type === "article" && m.url === url);
      if (prev) { prev.image = prev.image || (img ? bestSrc(img) : null); prev.title = prev.title || img?.getAttribute("alt") || txt(a); continue; }
      media.push({ type: "article", url, title: img?.getAttribute("alt") || "", image: img ? bestSrc(img) : null });
      found.add("article");
    }
    for (const a of sqa(card, "linkCard").filter((e) => !inQ(e) && e.querySelector("figure"))) {
      const img = a.querySelector("img") as HTMLImageElement | null;
      if (img) seenImg.add(img);
      const spans = [...a.querySelectorAll("p")].map((p) => txt(p.querySelector("span span") || p));
      media.push({ type: "link_preview", url: unwrap(a.getAttribute("href")!), title: spans[0] || "", subtitle: spans[1] || "", image: img ? bestSrc(img) : null });
      found.add("link_preview");
    }
    for (const v of sqa(card, "video").filter((e) => !inQ(e))) {
      const vid = v as HTMLVideoElement;
      const wrap = vid.closest('[role="region"]') || vid.parentElement!;
      const poster = (wrap.querySelector("img[src*='videocover']") as HTMLImageElement | null)?.src || vid.poster || "";
      const prog = (sq(wrap, "videoProgress")?.getAttribute("aria-valuetext") || "").match(/of (\d+):(\d+)/);
      wrap.querySelectorAll("img").forEach((i) => seenImg.add(i));
      media.push({ type: "video", poster, duration_s: prog ? +prog[1] * 60 + +prog[2] : isFinite(vid.duration) ? Math.round(vid.duration) : null, src: null, captions: [] });
      found.add("video");
    }
    let idx = 0;
    for (const img of sqa(card, "image") as HTMLImageElement[]) {
      if (inQ(img) || seenImg.has(img) || /profile-(display|framed)photo|company-logo/.test(img.src) || img.closest('a > div[aria-label], a:has(> figure) + div a')) continue;
      if (!/feedshare|image-shrink/.test(img.src)) { found.add("unclassified-image"); continue; }
      media.push({ type: "image", index: idx++, url: bestSrc(img), alt: img.getAttribute("alt") || "" });
      found.add("image");
    }
    let quote: any = null;
    if (quoted) {
      const qa_ = actors[1].closest("a") as HTMLAnchorElement;
      const qr = rich(sqa(quoted, "text")[0] || null);
      quote = { activity_urn: (qLink!.href.match(/urn:li:(?:activity|ugcPost|share):\d+/) || [null])[0], author: { name: firstText(actors[1]), profile_url: unwrap(qa_.getAttribute("href") || "") }, text: qr.text,
        images: (sqa(quoted, "image") as HTMLImageElement[]).filter((i) => /feedshare/.test(i.src)).map(bestSrc) };
    }
    const cnt = (key: string) => num(txt(sq(card, key)));
    return {
      activity_urn: isRepost ? null : activity || postUrn,
      post_urn: postUrn,
      repost_of: isRepost ? postUrn : null,
      layout: "sdui",
      kind: isRepost ? "repost" : quote ? "quote" : "original",
      author: { name, headline, profile_url: actorA ? unwrap(actorA.getAttribute("href") || "") : "" },
      time_text: txt(timeEl),
      edited: re("editedMarker", "").test(txt(timeEl)),
      text: r.text, html: r.html, links: r.links, mentions: r.mentions, hashtags: r.hashtags,
      media, media_types: [...found].filter((f) => f !== "unclassified-image"),
      unknown_components: found.has("unclassified-image") ? ["unclassified image (not a post image, card or video)"] : [],
      quote,
      counts: { reactions: cnt("reactions"), comments: cnt("comments") ?? 0, reposts: cnt("reposts") ?? 0, raw: "" },
      missing: [!postUrn && !activity && "urn", !actor && "actor", !textEl && !media.length && "text", !timeEl && "time"].filter(Boolean),
    };
  };

  (window as any).__lf = {
    missed,
    articleLinks: () => [...new Set(qa(document, "articleListLink").map((a) => unwrap((a as HTMLAnchorElement).href).split("?")[0].replace(/\/$/, "")))],
    // Classic cards first; else the server-driven layout. `layout` says which.
    activityCards: () => {
      const classic = qa(document, "activityCard").map((c) => ({ ...post(c), layout: "classic" }));
      return classic.length ? classic : sqa(document, "card").map((c) => sduiPost(c));
    },
    mainPost: () => { const c = qa(document, "activityCard")[0]; return c ? post(c) : null; },
    comments: (me: string) => qa(document, "comment").map((a) => comment(a, me)),
    commentCount: () => qa(document, "comment").length,
    threadCounts: () => counts(document),
    article: () => {
      const body = q(document, "articleBody");
      const cover = q(document, "articleCover") as HTMLImageElement | null;
      const figures = body ? [...body.querySelectorAll("figure")].map((f) => {
        const v = f.querySelector("video") as HTMLVideoElement | null;
        const isVideo = !!v || /video/i.test(f.getAttribute("data-type") || "") || !!f.querySelector("[class*='video']");
        const img = isVideo ? null : (f.querySelector("img") as HTMLImageElement | null);
        return { kind: isVideo ? "video" : "image", src: img?.src || null, poster: v?.poster || (f.querySelector("img") as HTMLImageElement | null)?.src || null,
          duration_s: v && isFinite(v.duration) ? Math.round(v.duration) : null, caption: txt(f.querySelector("figcaption")), alt: img?.getAttribute("alt") || "" };
      }) : [];
      const iframes = body ? [...body.querySelectorAll("iframe")].map((f) => (f as HTMLIFrameElement).src) : [];
      const links = body ? [...body.querySelectorAll("a[href]")].map((a) => ({ text: txt(a), url: unwrap(a.getAttribute("href")!) })) : [];
      return {
        title: txt(q(document, "articleTitle")),
        subtitle: txt(q(document, "articleSubtitle")) || null,
        cover: cover ? cover.src : null,
        date_text: txt(q(document, "articleDate")),
        edited_text: (txt(q(document, "articleDate")).match(/(edited|updated)[^•]*/i) || [null])[0],
        body_html: body ? body.innerHTML : "",
        body_text: body ? (body as HTMLElement).innerText : "",
        figures, iframes, links,
        counts: counts(document),
        canonical: (document.querySelector("link[rel=canonical]") as HTMLLinkElement | null)?.href || location.href,
      };
    },
    // Visible expanders by kind, for the expansion loop and the self-check.
    expanders: () => {
      const out: Record<string, number> = {};
      const skip = new RegExp(S.expanderSkipSource, "i");
      for (const [k, spec] of Object.entries(S.expanders as Record<string, any>)) {
        const label = new RegExp(spec.labelSource, "i");
        let n = 0;
        for (const s of spec.sel) {
          try { n = [...document.querySelectorAll(s)].filter((e) => { const t = ((e as HTMLElement).innerText || "").trim(); return (e as HTMLElement).offsetParent && !skip.test(t) && (label.test(t) || label.test(e.getAttribute("aria-label") || "")); }).length; } catch { n = 0; }
          if (n) break;
        }
        out[k] = n;
      }
      return out;
    },
  };
}

// Expand every comment and reply on the current page: switch to "Most
// recent", then click "Load more comments" and "See previous replies"
// until none are left, re-querying after each click (LinkedIn re-renders).
export async function expandThread(s: Session, maxClicks: number, timeBudgetMs: number) {
  const page = s.page;
  const log = { sort: "most_relevant(default)", clicks: {} as Record<string, number>, stuck: [] as string[], left: {} as Record<string, number>, see_more: "text already in DOM; not clicked" };
  const t0 = Date.now();
  const count = () => page.evaluate(() => (window as any).__lf.commentCount() as number);
  const firstVisible = async (kind: keyof typeof SEL.expanders) => {
    const spec = SEL.expanders[kind];
    for (const sel of spec.sel) {
      for (const e of await page.$$(sel)) {
        const st = await e.evaluate((x: Element) => ({ v: !!(x as HTMLElement).offsetParent, t: ((x as HTMLElement).innerText || "").trim(), a: x.getAttribute("aria-label") || "" }));
        if (!st.v || SEL.expanderSkip.test(st.t) || !(spec.label.test(st.t) || spec.label.test(st.a))) continue;
        return e;
      }
    }
    return null;
  };

  // Sort: "Most recent" lists every comment in order; "Most relevant" may
  // filter some. If the switch fails we keep the default and say so.
  const trigger = await firstVisible("sortTrigger");
  if (trigger && (await s.safeClick(trigger, "sortTrigger"))) {
    const opt = await (async () => {
      for (let i = 0; i < 10; i++) {
        for (const sel of SEL.expanders.sortMostRecent.sel) {
          for (const e of await page.$$(sel)) {
            const t = await e.evaluate((x: Element) => ((x as HTMLElement).innerText || "").trim());
            if (/most recent/i.test(t) && (await e.evaluate((x: Element) => !!(x as HTMLElement).offsetParent))) return e;
          }
        }
        await sleep(300);
      }
      return null;
    })();
    if (opt && (await s.safeClick(opt, "sortMostRecent"))) {
      await sleep(2500);
      log.sort = "most_recent";
    } else {
      await page.keyboard.press("Escape");
      log.sort = "most_relevant(switch failed)";
    }
  }

  const order: (keyof typeof SEL.expanders)[] = ["loadMoreComments", "previousReplies"];
  let noEffect = 0;
  while (s.clicks < 1e9) {
    if (Date.now() - t0 > timeBudgetMs) { log.stuck.push("time budget"); break; }
    const total = Object.values(log.clicks).reduce((a, b) => a + b, 0);
    if (total >= maxClicks) { log.stuck.push("click cap"); break; }
    // Lazy loading: scroll to the end of the comment list first.
    await s.scrollGradually(3);
    let clicked: string | null = null;
    for (const kind of order) {
      const el = await firstVisible(kind);
      if (!el) continue;
      const before = await count();
      if (!(await s.safeClick(el, kind))) { s.opts.log({ ev: "skip-expander", kind, label: await el.evaluate((x: Element) => `${((x as HTMLElement).innerText || "").trim()} | ${x.getAttribute("aria-label") || ""}`) }); continue; }
      clicked = kind;
      log.clicks[kind] = (log.clicks[kind] || 0) + 1;
      // Wait for the effect: more comments, or the button gone.
      let changed = false;
      for (let i = 0; i < 30 && !changed; i++) {
        await sleep(250);
        changed = (await count()) > before || !(await el.evaluate((x: Element) => document.contains(x) && !!(x as HTMLElement).offsetParent).catch(() => false));
      }
      noEffect = changed ? 0 : noEffect + 1;
      break;
    }
    if (!clicked) break;
    if (noEffect >= 2) { log.stuck.push(`${clicked} had no effect twice`); break; }
  }
  (log as any).left_labels = (await page.evaluate((sels: string[]) => sels.flatMap((s) => [...document.querySelectorAll(s)].filter((e) => (e as HTMLElement).offsetParent).map((e) => `${((e as HTMLElement).innerText || "").trim()} | ${e.getAttribute("aria-label") || ""}`)), [...SEL.expanders.loadMoreComments.sel, ...SEL.expanders.previousReplies.sel])).filter((l: string) => !SEL.expanderSkip.test(l.split(" | ")[0]));
  log.left = Object.fromEntries(Object.entries(await page.evaluate(() => (window as any).__lf.expanders() as Record<string, number>)).filter(([k, n]) => n > 0 && ["loadMoreComments", "previousReplies"].includes(k)));
  return log;
}

// Open each post image in LinkedIn's viewer to read the larger copy's URL
// (the feed shows an 800-px copy). Escape closes the viewer.
export async function upgradeImages(s: Session, max: number): Promise<string[]> {
  const page = s.page;
  const out: string[] = [];
  const buttons = await page.$$(SEL.expanders.imageLightbox.sel[0]);
  for (const b of buttons.slice(0, max)) {
    if (await b.evaluate((x: Element) => !!x.closest(".feed-shared-update-v2__update-content-wrapper"))) { out.push(""); continue; }
    if (!(await s.safeClick(b, "imageLightbox"))) { out.push(""); continue; }
    let src = "";
    for (let i = 0; i < 20 && !src; i++) {
      await sleep(300);
      src = await page.evaluate((sels: string[]) => {
        for (const s of sels) { const i = document.querySelector(s) as HTMLImageElement | null; if (i && i.complete && i.naturalWidth > 0) return i.src; }
        return "";
      }, SEL.lightboxImage);
    }
    out.push(src);
    await page.keyboard.press("Escape");
    await sleep(jitter(700, 1200));
  }
  return out;
}
