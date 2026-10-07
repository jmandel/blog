#!/usr/bin/env node
// Live fetch of Josh's own LinkedIn articles, posts and their comment
// threads through an already logged-in browser, written as a LinkedIn
// export (Articles/Articles/*.html, Shares.csv, Rich_Media.csv) plus a
// Live/ sidecar with what the export leaves out. See AGENTS.md
// "LinkedIn live fetch" for the runbook.
//
//   node scripts/linkedin_live_fetch.ts --probe
//   node scripts/linkedin_live_fetch.ts --only <url> [--only <url> ...]
//   node scripts/linkedin_live_fetch.ts --articles --posts --since 2026-09-01
//   ./scripts/local-import.sh linkedin_work/live/linkedin-live.zip
//
// Read-only on LinkedIn: it navigates, scrolls and clicks only the
// expanders listed in scripts/linkedin_live/selectors.ts.

import { parseArgs } from "node:util";
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync, readFileSync, existsSync, readdirSync, rmSync, appendFileSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { execFileSync } from "node:child_process";
import { Session, Blocked, BudgetExceeded, expandThread, upgradeImages } from "./linkedin_live/page.ts";
import { idTime, SEL } from "./linkedin_live/selectors.ts";
import { loadBlog, findClaim, missingBlocks, type BlogEntry } from "./linkedin_live/blog.ts";

const { values: args } = parseArgs({
  options: {
    articles: { type: "boolean", default: false },
    posts: { type: "boolean", default: false },
    since: { type: "string" },
    only: { type: "string", multiple: true, default: [] },
    out: { type: "string", default: "linkedin_work/live" },
    "blog-dir": { type: "string", default: "." },
    "max-pages": { type: "string", default: "150" },
    "max-clicks": { type: "string", default: "80" },
    "cdp-url": { type: "string", default: "http://127.0.0.1:9333" },
    profile: { type: "string" },
    refetch: { type: "boolean", default: false },
    "build-only": { type: "boolean", default: false },
    probe: { type: "boolean", default: false },
    "dry-run": { type: "boolean", default: false },
    "no-threads": { type: "boolean", default: false },
    "extract-file": { type: "string" },
    "capture-video": { type: "string", multiple: true, default: [] },
    "min-delay": { type: "string", default: "3000" },
    "max-delay": { type: "string", default: "6500" },
    help: { type: "boolean", short: "h", default: false },
  },
});

if (args.help) {
  console.log(readFileSync(new URL(import.meta.url), "utf8").split("\n").slice(1, 16).join("\n"));
  process.exit(0);
}

const BLOG = resolve(args["blog-dir"]!);
// A probe writes to its own folder so it never mixes with a real run.
const OUT = resolve(BLOG, args.probe && args.out === "linkedin_work/live" ? "linkedin_work/live-probe" : args.out!);
const LIVE = join(OUT, "Live");
const ITEMS = join(LIVE, "items");
const MEDIA = join(LIVE, "media");
const STATE_FILE = join(BLOG, "linkedin_work", "live_state.json");
const PROBE_PAGES = {
  article: "https://www.linkedin.com/pulse/medicare-wants-rein-at-home-health-monitoring-cutting-josh-mandel-md-pjhwc/",
  post: "https://www.linkedin.com/feed/update/urn:li:activity:7512888792354275328/",
};

mkdirSync(ITEMS, { recursive: true });
mkdirSync(MEDIA, { recursive: true });
const LOG = join(LIVE, "log.jsonl");
const log = (rec: Record<string, unknown>) => {
  const line = JSON.stringify({ t: new Date().toISOString(), ...rec });
  appendFileSync(LOG, line + "\n");
  if (rec.ev !== "load") console.log(`  ${rec.ev}: ${Object.entries(rec).filter(([k]) => k !== "ev").map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`).join(" ")}`);
  else console.log(`[${rec.n}] ${rec.kind} ${rec.url}`);
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const sha = (b: Buffer | string) => createHash("sha256").update(b).digest("hex");
const readJson = (p: string, dflt: any = null) => (existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : dflt);
const writeJson = (p: string, v: unknown) => { mkdirSync(dirname(p), { recursive: true }); writeFileSync(p, JSON.stringify(v, null, 2) + "\n"); };
const iso = (d: Date | null) => (d ? d.toISOString().replace(/\.\d{3}Z$/, "Z") : null);
const urnId = (urn: string | null | undefined) => (urn || "").match(/(\d{10,})/)?.[1] || "";
const threadKey = (urn: string) => urn.replace(/^urn:li:/, "").replace(/[^A-Za-z0-9]+/g, "-");
const normText = (s: string) => s.replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/\s+/g, " ").trim();
const basenameOf = (pulseUrl: string) => (pulseUrl.match(/\/pulse\/([^/?#]+)/)?.[1] || "").replace(/\/$/, "");
// An activity and the ugcPost/share it wraps are created within the same
// second or so; that's how an article's thread is tied to its post.
const sameTime = (a: string | null | undefined, b: string | null | undefined) => {
  const x = idTime(urnId(a)), y = idTime(urnId(b));
  return !!x && !!y && Math.abs(x.getTime() - y.getTime()) < 5000;
};
const idOf = (basename: string) => basename.match(/-([a-z0-9]{5})$/)?.[1] || "";
const extFor = (type: string, url: string) =>
  /png/.test(type) ? ".png" : /gif/.test(type) ? ".gif" : /webp/.test(type) ? ".webp" : /vtt/.test(type) ? ".vtt" : /pdf/.test(type) ? ".pdf" : /mp4/.test(type) ? ".mp4" : /svg/.test(type) ? ".svg" : /jpe?g/.test(type) ? ".jpg" : (url.match(/\.(png|gif|jpe?g|webp|pdf|vtt)(\?|$)/)?.[0].replace(/\?$/, "") || ".jpg");
const fmtExport = (d: Date) => d.toISOString().slice(0, 16).replace("T", " "); // "2026-02-11 19:59"
const fmtShareDate = (d: Date) => new Date(Math.floor(d.getTime() / 1000) * 1000).toISOString().slice(0, 19).replace("T", " ");

// Largest copy of each LinkedIn image asset named anywhere in the page
// (DOM, embedded JSON): asset id → URL. Sizes are in the path (shrink_W_H).
function bestImageUrls(html: string): Map<string, string> {
  const text = html.replace(/\\u0026/g, "&").replace(/&amp;amp;/g, "&").replace(/&amp;/g, "&").replace(/\\\//g, "/");
  const best = new Map<string, { url: string; area: number }>();
  const re = /https:\/\/media\.licdn\.com\/dms\/image\/(?:sync\/)?v2\/([A-Za-z0-9_-]+)\/([a-z_-]+?)-shrink_(\d+)(?:_(\d+))?\/[^"'\s\\<>()]+/g; // no ")" (CSS url(...))
  for (const m of text.matchAll(re)) {
    if (!/[?&]t=/.test(m[0])) continue; // unsigned fragments 404
    const area = Number(m[3]) * Number(m[4] || m[3]);
    const cur = best.get(m[1]);
    if (!cur || area > cur.area) best.set(m[1], { url: m[0], area });
  }
  return new Map([...best].map(([k, v]) => [k, v.url]));
}
const assetOf = (url: string) => url.match(/\/dms\/image\/(?:sync\/)?v2\/([A-Za-z0-9_-]+)\//)?.[1] || "";

// ---------------------------------------------------------------------------
// State, blog knowledge
// ---------------------------------------------------------------------------
const state = readJson(STATE_FILE, { articles: {}, profile_url: null });
const blog: BlogEntry[] = loadBlog(BLOG);
const knownArticleIds = new Set(blog.filter((e) => e.kind !== "share").flatMap((e) => [e.linkedin_id, idOf(basenameOf(e.original_url || "")), ...e.claims.map((c) => (c.match(/-([a-z0-9]{5})\/?$/) || c.match(/^([a-z0-9]{5})$/) || [])[1])]).filter(Boolean) as string[]);
const knownShareIds = new Set(blog.flatMap((e) => [e.share_id, e.intro_share_id]).filter(Boolean) as string[]);
const shareDates = blog.filter((e) => e.kind === "share" && e.date).map((e) => e.date!).sort();

// ---------------------------------------------------------------------------
// Fetchers (browser)
// ---------------------------------------------------------------------------
interface Ctx { s: Session; me: string; report: any[] }

// Download a media file chosen from a specific element. `from` names that
// element (provenance); a file without it is refused, and the report FAILs
// any media record that lacks it.
async function saveMedia(ctx: Ctx, url: string | null | undefined, role: string, failures: string[], from?: string) {
  if (!url) return null;
  if (!from) { failures.push(`${role}: no element provenance; refused`); return null; }
  const got = await ctx.s.downloadMedia(url);
  if ("error" in got) { failures.push(`${role}: ${url.slice(0, 100)} (${got.error})`); return null; }
  const h = sha(got.body);
  const ext = extFor(got.type, url);
  const file = `${h.slice(0, 16)}${ext}`;
  if (!existsSync(join(MEDIA, file))) writeFileSync(join(MEDIA, file), got.body);
  return { file: `Live/media/${file}`, sha256: h, bytes: got.body.length, content_type: got.type.split(";")[0], source_url: url, via: got.via, from };
}

async function captureThread(ctx: Ctx, subject: any, html: string) {
  const s = ctx.s;
  if (args["no-threads"]) return null;
  const counts = await s.page.evaluate(() => (window as any).__lf.threadCounts());
  // Same thread already captured complete this run (an article and the post
  // announcing it show one thread): reuse it instead of expanding again.
  for (const f of existsSync(join(LIVE, "threads")) ? readdirSync(join(LIVE, "threads")) : []) {
    const t = readJson(join(LIVE, "threads", f));
    const fresh = t?.fetched_at && Date.now() - Date.parse(t.fetched_at) < 6 * 3600_000;
    const sameSubject = t?.subjects?.some((x: any) => (subject.activity_urn && x.activity_urn === subject.activity_urn));
    if (!args.refetch && !args.probe && fresh && t.complete && sameSubject && t.captured.total === counts.comments) {
      log({ ev: "thread-reused", urn: t.thread_urn, captured: t.captured.total });
      return { ...t, subjects: [subject] };
    }
  }
  const expand = (counts.comments ?? 0) > 0 ? await expandThread(s, Number(args["max-clicks"]), 4 * 60_000) : { sort: "n/a (no comments)", clicks: {}, stuck: [], left: {} };
  const raw: any[] = await s.page.evaluate((me: string) => (window as any).__lf.comments(me), ctx.me);
  const html2 = await s.page.content();
  // Thread URN: the post every comment hangs off; otherwise the
  // ugcPost/share URN named most often on the page.
  let thread = raw[0]?.id?.match(/urn:li:comment:\((\w+):(\d+),/);
  let threadUrn = thread ? `urn:li:${thread[1]}:${thread[2]}` : null;
  if (!threadUrn) {
    const freq = new Map<string, number>();
    for (const m of (html + html2).matchAll(/urn:li:(ugcPost|share):(\d{15,})/g)) freq.set(m[0], (freq.get(m[0]) || 0) + 1);
    const want = subject.activity_urn ? idTime(urnId(subject.activity_urn))?.getTime() : null;
    const cands = [...freq.entries()].sort((a, b) => b[1] - a[1]).map(([u]) => u);
    // Prefer the URN created within seconds of the activity.
    threadUrn = (want && cands.find((u) => Math.abs((idTime(urnId(u))?.getTime() || 0) - want) < 5000)) || cands[0] || null;
  }
  const seen = new Set<string>();
  const comments: any[] = [];
  const mediaFail: string[] = [];
  for (const c of raw) {
    const id = c.id || "h:" + sha(`${c.author.profile_url}|${c.text}`).slice(0, 16);
    if (seen.has(id)) continue;
    seen.add(id);
    const cid = id.match(/,(\d+)\)$/)?.[1];
    const media = [];
    for (const m of c.media) {
      if (m.type === "image" || m.type === "gif") media.push({ ...m, ...(await saveMedia(ctx, m.url, "comment media", mediaFail, m.from)) });
      else media.push(m);
    }
    comments.push({ ...c, id, created_at: iso(cid ? idTime(cid) : null), media });
  }
  comments.sort((a, b) => (a.created_at || "").localeCompare(b.created_at || ""));
  const top = comments.filter((c) => !c.parent_id);
  const tree = top.map((t) => ({ id: t.id, replies: comments.filter((c) => c.parent_id === t.id).map((r) => r.id) }));
  const shortReplies = top.filter((t) => t.replies_displayed != null && comments.filter((c) => c.parent_id === t.id).length < t.replies_displayed).map((t) => t.id);
  const displayed = counts.comments ?? null;
  const captured = comments.length;
  const snap = {
    schema: "linkedin-thread/1",
    thread_urn: threadUrn,
    url: threadUrn ? `https://www.linkedin.com/feed/update/${threadUrn}/` : null,
    subjects: [subject],
    fetched_at: iso(new Date()),
    sort: expand.sort,
    displayed: { comments: displayed, reactions: counts.reactions, reposts: counts.reposts },
    captured: { total: captured, top_level: top.length, replies: captured - top.length },
    complete: displayed == null ? captured === 0 : captured >= displayed && shortReplies.length === 0,
    expanders_used: expand.clicks, expanders_left: expand.left, expanders_left_labels: (expand as any).left_labels || [], stuck: expand.stuck,
    replies_short_on: shortReplies,
    media_failures: mediaFail,
    comments, tree,
  };
  log({ ev: "thread", urn: threadUrn, displayed, captured, top: top.length, sort: expand.sort, clicks: expand.clicks, left: expand.left, media_failed: mediaFail.length });
  return snap;
}

function writeThread(snap: any) {
  if (!snap?.thread_urn) return;
  const p = join(LIVE, "threads", threadKey(snap.thread_urn) + ".json");
  const old = readJson(p);
  // Same thread captured from two pages (article + its post) in one run:
  // keep the union, preferring the more complete capture's fields.
  if (old && old.fetched_at && Date.now() - Date.parse(old.fetched_at) < 6 * 3600_000) {
    const byId = new Map(old.comments.map((c: any) => [c.id, c]));
    for (const c of snap.comments) byId.set(c.id, c);
    snap.comments = [...byId.values()].sort((a: any, b: any) => (a.created_at || "").localeCompare(b.created_at || ""));
    const subj = [...old.subjects, ...snap.subjects];
    snap.subjects = subj.filter((x, i) => subj.findIndex((y) => JSON.stringify(y) === JSON.stringify(x)) === i);
    const top = snap.comments.filter((c: any) => !c.parent_id);
    snap.tree = top.map((t: any) => ({ id: t.id, replies: snap.comments.filter((c: any) => c.parent_id === t.id).map((r: any) => r.id) }));
    snap.captured = { total: snap.comments.length, top_level: top.length, replies: snap.comments.length - top.length };
    snap.complete = snap.complete || old.complete || (snap.displayed.comments != null && snap.comments.length >= snap.displayed.comments);
  }
  writeJson(p, snap);
}

// An item that can't be trusted (wrong page, identity mismatch). The run
// records it as FAIL and moves on; nothing from it is written.
class ItemError extends Error {}
const itemFailures: { item: string; title: string; status: string; fails: string[]; warns: string[] }[] = [];
async function guarded<T>(item: string, fn: () => Promise<T>): Promise<T | null> {
  try { return await fn(); } catch (e) {
    if (!(e instanceof ItemError)) throw e;
    itemFailures.push({ item, title: "", status: "FAIL", fails: [e.message], warns: [] });
    log({ ev: "item-failed", item, error: e.message });
    return null;
  }
}

const normTitle = (t: string) => normText(t || "").toLowerCase().replace(/[^a-z0-9 ]/g, "").replace(/\s+/g, " ").trim();
const decodeEntities = (s: string) => s.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;|&#x27;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");

// The logged-out public page of an article: an independent view of its
// title, cover and dates. Plain HTTP, no cookies, paced like a page load.
async function publicArticle(ctx: Ctx, basename: string) {
  const s = ctx.s;
  const url = `https://www.linkedin.com/pulse/${basename}`;
  if (s.pageLoads >= s.opts.maxPages) throw new BudgetExceeded(`page budget reached before public check of ${basename}`);
  await s.pace();
  s.pageLoads++;
  s.lastLoad = Date.now();
  log({ ev: "load", n: s.pageLoads, kind: "public-article", url });
  const r = await fetch(url, { headers: { "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36", "accept-language": "en-US,en" }, redirect: "follow" });
  const html = await r.text();
  const meta = (p: string) => decodeEntities(html.match(new RegExp(`<meta[^>]*(?:property|name)="${p}"[^>]*content="([^"]*)"`))?.[1] || html.match(new RegExp(`<meta[^>]*content="([^"]*)"[^>]*(?:property|name)="${p}"`))?.[1] || "") || null;
  let ld: any = null;
  for (const m of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) { try { const d = JSON.parse(m[1]); if (d["@type"] === "Article") ld = d; } catch { /* skip */ } }
  const coverUrl = decodeEntities(html.match(SEL.publicCover)?.[1] || "") || null;
  const ogImage = meta("og:image");
  // Native videos in the body: <video data-poster-url data-digitalmedia-asset-urn>.
  const videoPosters: Record<string, string> = {};
  for (const m of html.matchAll(/<video\b[^>]*>/g)) {
    const poster = m[0].match(/data-poster-url="([^"]+)"/)?.[1];
    const asset = m[0].match(/urn:li:digitalmediaAsset:([A-Za-z0-9_-]+)/)?.[1];
    if (poster && asset) videoPosters[asset] = decodeEntities(poster);
  }
  return {
    video_posters: videoPosters,
    status: r.status, final_url: r.url, og_title: meta("og:title"), og_image: ogImage,
    name: ld?.name || null, date_published: ld?.datePublished || null, date_modified: ld?.dateModified || null,
    comment_count: ld?.commentCount != null ? Number(ld.commentCount) : null,
    // The article's own cover, from its figure.cover-img, else JSON-LD
    // image, else og:image when it is an article-cover_image.
    cover_url: coverUrl || ld?.image?.url || (ogImage && /article-cover_image/.test(ogImage) ? ogImage : null),
    cover_from: coverUrl ? "public page figure.cover-img" : ld?.image?.url ? "public page JSON-LD image" : ogImage && /article-cover_image/.test(ogImage) ? "public page og:image" : null,
    og_image_kind: !ogImage ? "none" : /article-cover_image/.test(ogImage) ? "cover" : /playlist\/vid|videocover/.test(ogImage) ? "video thumbnail" : /profile-displayphoto|\.svg|static\.licdn/.test(ogImage) ? "placeholder" : "other",
    fetched_at: iso(new Date()),
  };
}

async function fetchArticle(ctx: Ctx, url: string) {
  const s = ctx.s;
  const basename = basenameOf(url);
  const lid = idOf(basename);
  await s.goto(`https://www.linkedin.com/pulse/${basename}/`, "article");
  await s.scrollGradually(14);
  const a = await s.page.evaluate(() => (window as any).__lf.article());
  // 1. Is this page the article we asked for? A wrong or old slug can land
  //    on /feed/, where other articles' covers load.
  const finalPath = new URL(a.final_url).pathname.replace(/\/$/, "");
  if (!/^\/pulse\//.test(finalPath) || idOf(basenameOf(a.final_url)) !== lid || /article_not_found|\/feed\b/.test(a.final_url)) {
    throw new ItemError(`article ${lid}: landed on ${finalPath}, not /pulse/${basename}`);
  }
  if (!a.title) throw new ItemError(`article ${lid}: no title on the page (selectors.ts: articleTitle)`);
  const known = blog.find((e) => e.kind !== "share" && (e.linkedin_id === lid || idOf(basenameOf(e.original_url || "")) === lid));
  const html = await s.page.content();
  // 2. The stored article HTML: the embedded object whose title is this
  //    page's title (the page also embeds other articles).
  const codeJson: string = await s.page.evaluate(() => [...document.querySelectorAll("code")].map((c) => c.textContent || "").filter((t) => t.includes("contentHtml")).join("\n"));
  let contentHtml: string | null = null;
  let publishedAt: number | null = null;
  let articleUrn: string | null = null;
  const bodyStart = normTitle(a.body_text).slice(0, 120);
  for (const block of codeJson.split("\n").filter(Boolean)) {
    try {
      const walk = (o: any) => {
        if (!o || typeof o !== "object") return;
        // Ours if its title is this page's title, or (no title on the object)
        // its text starts like this page's article body.
        const same = typeof o.contentHtml === "string" && (normTitle(o.title || "") === normTitle(a.title)
          || (!o.title && bodyStart.length > 40 && normTitle(o.contentHtml.replace(/<[^>]+>/g, " ").replace(/&[a-z#0-9]+;/g, " ")).includes(bodyStart)));
        if (same && !contentHtml) {
          contentHtml = o.contentHtml;
          if (typeof o.publishedAt === "number") publishedAt = o.publishedAt;
          const u = JSON.stringify(o).match(/urn:li:linkedInArticle:\d+/);
          if (u) articleUrn = u[0];
        }
        for (const v of Object.values(o)) walk(v);
      };
      walk(JSON.parse(block));
    } catch { /* not JSON */ }
  }
  const checks: string[] = [];
  // LinkedIn's stored HTML (also what the export contains) can silently
  // lose code blocks and inline code; the rendered body has them. If the
  // stored copy is missing words the page shows, use the rendered body.
  let bodyLoss = 0;
  if (contentHtml) {
    const UI = new Set(["captions", "are", "auto", "generated", "play", "see", "content", "credentials", "video", "player", "loaded", "seconds"]);
    const toks = (t: string) => decodeEntities(t).toLowerCase().replace(/[‘’]/g, "'").match(/[a-z0-9]+/g) || [];
    const stored = new Map<string, number>();
    for (const w of toks((contentHtml as string).replace(/<[^>]+>/g, " "))) stored.set(w, (stored.get(w) || 0) + 1);
    for (const w of toks(a.body_text)) { const n = stored.get(w) || 0; if (n > 0) stored.set(w, n - 1); else if (!UI.has(w)) bodyLoss++; }
    if (bodyLoss > 10) { checks.push(`stored article HTML is missing ${bodyLoss} words the page shows (code?); used the rendered body`); contentHtml = null; }
  }
  const activities = (() => { const f = new Map<string, number>(); for (const m of html.matchAll(/urn:li:activity:\d{15,}/g)) f.set(m[0], (f.get(m[0]) || 0) + 1); return [...f].sort((x, y) => y[1] - x[1]).map(([u]) => u); })();
  let activity = activities[0] || null;
  // 3. Independent cross-check against the logged-out public page.
  const pub: any = await publicArticle(ctx, basename);
  // Some articles aren't visible logged out ("article_not_found", sign-up
  // wall). Then there's nothing to cross-check: keep the logged-in identity
  // checks, take the cover only from the article's own header, and WARN.
  pub.unavailable = /article_not_found|\/(signup|login|authwall)/.test(pub.final_url);
  if (pub.unavailable) {
    checks.push(`not publicly visible (${new URL(pub.final_url).pathname}); no public cross-check`);
    pub.cover_url = null; pub.cover_from = null; pub.og_image_kind = "unavailable";
  } else {
    if (pub.status !== 200 || idOf(basenameOf(pub.final_url)) !== lid) throw new ItemError(`article ${lid}: public page ${pub.status} at ${pub.final_url}`);
    const pubTitle = pub.name || pub.og_title || "";
    if (normTitle(pubTitle) !== normTitle(a.title)) throw new ItemError(`article ${lid}: title "${a.title}" but the public page says "${pubTitle}"`);
  }
  if (known && normTitle(known.title) !== normTitle(a.title)) checks.push(`title changed on LinkedIn: blog has "${known.title}"`);
  // 4. Cover: this article's header image, which must be the public page's
  //    own cover. Network traffic is never a source, only a download path.
  const best = bestImageUrls(html + (contentHtml || ""));
  const failures: string[] = [];
  const hdrAsset = a.cover ? assetOf(a.cover) : null;
  const pubAsset = pub.cover_url ? assetOf(pub.cover_url) : null;
  let coverPick: { url: string; from: string } | null = null;
  if (hdrAsset && pubAsset && hdrAsset !== pubAsset) throw new ItemError(`article ${lid}: header cover ${hdrAsset} differs from the public page's cover ${pubAsset}`);
  if (hdrAsset && !pubAsset && !pub.unavailable && pub.og_image_kind !== "cover") throw new ItemError(`article ${lid}: header has cover ${hdrAsset} but the public page shows none (og:image is ${pub.og_image_kind})`);
  if (hdrAsset) coverPick = { url: best.get(hdrAsset) || a.cover, from: pub.unavailable ? `${a.cover_from}; no public page to confirm` : `${a.cover_from}; confirmed by ${pub.cover_from}` };
  else if (pubAsset) coverPick = { url: pub.cover_url!, from: pub.cover_from! };
  const cover = coverPick ? await saveMedia(ctx, coverPick.url, "cover", failures, coverPick.from) : null;
  // 5. Inline images: figures inside the article body whose asset is in the
  //    article's stored HTML.
  const images = [];
  const videos = [];
  for (const f of a.figures) {
    if (f.kind === "video") {
      // Native video in an article: poster, duration, captions; no file.
      // The poster is the video's chosen cover (videocover-high) for the
      // same video asset when the page names it, else the figure's frame.
      const asset = f.poster ? (assetOf(f.poster) || (f.poster.match(/\/playlist\/vid\/v2\/([A-Za-z0-9_-]+)\//) || [])[1] || "") : "";
      const cover = asset ? (html + (contentHtml || "")).replace(/&amp;/g, "&").match(new RegExp(`https://media\\.licdn\\.com/dms/image/v2/${asset}/videocover-high/[^"'\\s\\\\<>()]+`))?.[0] : null;
      const pubPoster = asset ? pub.video_posters?.[asset] : null;
      if (pubPoster) f.poster = pubPoster;
      else if (cover) f.poster = cover;
      const posterFrom = pubPoster ? `public page <video data-poster-url> for video asset ${asset}` : cover ? `videocover of video asset ${asset} (from its figure)` : `poster of video figure in article body`;
      const vtt = asset ? [...s.mediaCache.keys()].find((u) => /webvtt/.test(u) && u.includes(asset)) : undefined;
      videos.push({ index: videos.length + 1, caption: f.caption || null, duration_s: f.duration_s, poster_file: await saveMedia(ctx, f.poster, "article video poster", failures, posterFrom), captions_file: vtt ? await saveMedia(ctx, vtt, "captions", failures, `captions of video asset ${asset} (from its figure)`) : null, download: "not available: streamed as segments" });
      continue;
    }
    const asset = f.src ? assetOf(f.src) : null;
    if (asset && contentHtml && !(contentHtml as string).includes(asset)) { failures.push(`image ${asset}: in the page's article body but not in the article's stored HTML; skipped`); continue; }
    const src = f.src ? best.get(asset!) || f.src : null;
    images.push({ index: images.length + 1, asset, caption: f.caption || null, alt: f.alt || null, ...(await saveMedia(ctx, src, `image ${images.length + 1}`, failures, `${f.from} #${images.length + 1}`)) });
  }
  const thread = await captureThread(ctx, { kind: "article", linkedin_id: lid, url: `https://www.linkedin.com/pulse/${basename}`, activity_urn: activity }, html);
  writeThread(thread);
  // The announcing post: the activity created with the thread's post if
  // one is named, else the activity the page names most often. (A scheduled
  // post's activity can be a day younger than its ugcPost, so time alone
  // isn't enough; the post page's thread URN settles it in build().)
  if (thread?.thread_urn) activity = activities.find((u) => sameTime(u, thread.thread_urn)) || activity;
  const threadPost = thread?.thread_urn ? idTime(urnId(thread.thread_urn)) : null;
  const createdAt = articleUrn ? idTime(urnId(articleUrn)) : null;
  const publishedIso = iso(publishedAt ? new Date(publishedAt) : threadPost);
  if (pub.date_published && publishedIso && Math.abs(Date.parse(pub.date_published) - Date.parse(publishedIso)) > 5 * 60_000) checks.push(`published ${publishedIso} but the public page says ${pub.date_published}`);
  if (pub.comment_count != null && thread && thread.displayed.comments != null && pub.comment_count !== thread.displayed.comments) checks.push(`public page counts ${pub.comment_count} comments, the logged-in page ${thread.displayed.comments}`);
  const item = {
    kind: "article",
    fetched_at: iso(new Date()),
    url: `https://www.linkedin.com/pulse/${basename}`,
    final_url: a.final_url,
    basename, linkedin_id: lid, article_urn: articleUrn,
    title: a.title, subtitle: a.subtitle,
    created_at: iso(createdAt),
    published_at: publishedIso,
    date_text: a.date_text, edited_text: a.edited_text,
    body_source: contentHtml ? "embedded contentHtml (matched by title)" : bodyLoss > 10 ? `DOM .reader-article-content (stored HTML missing ${bodyLoss} words)` : "DOM .reader-article-content",
    body_html: contentHtml || a.body_html,
    text: a.body_text,
    text_hash: sha(normText(a.body_text)),
    cover: cover ? { ...cover, asset: assetOf(coverPick!.url) } : null,
    cover_media: cover ? "image" : pub.og_image_kind === "video thumbnail" ? "video (no cover image)" : "none",
    public_check: pub,
    checks,
    images, videos, iframes: a.iframes, links: a.links,
    intro_activity_urn: activity, thread_urn: thread?.thread_urn || null,
    counts: a.counts,
    media_failures: failures,
  };
  writeJson(join(ITEMS, `article-${lid || sha(basename).slice(0, 8)}.json`), item);
  log({ ev: "article", id: lid, title: item.title.slice(0, 60), body_chars: item.text.length, images: images.length, cover: cover ? coverPick!.from : item.cover_media, media_failed: failures.length, thread: item.thread_urn, source: item.body_source, checks });
  return item;
}

async function resolveShortLinks(ctx: Ctx, links: any[]) {
  for (const l of links) {
    if (!/^https?:\/\/lnkd\.in\//.test(l.url) || l.resolved) continue;
    if (ctx.s.pageLoads >= Number(args["max-pages"])) break;
    await ctx.s.pace();
    ctx.s.pageLoads++;
    ctx.s.lastLoad = Date.now();
    log({ ev: "load", n: ctx.s.pageLoads, kind: "lnkd.in", url: l.url });
    try {
      const r = await fetch(l.url, { redirect: "manual", headers: { "user-agent": "Mozilla/5.0" } });
      let target = r.headers.get("location");
      if (!target) { const body = await r.text(); target = body.match(/<a[^>]+data-tracking-control-name="external_url_click"[^>]+href="([^"]+)"/)?.[1] || body.match(/href="(https?:\/\/(?!lnkd\.in|[\w.]*linkedin\.com)[^"]+)"/)?.[1] || null; }
      if (target) l.resolved = target.replace(/&amp;/g, "&");
    } catch { /* leave unresolved */ }
  }
}

const fetchedThisRun = new Set<string>();
async function fetchPost(ctx: Ctx, activityUrn: string, card: any | null) {
  const s = ctx.s;
  // Each post at most once per run (an article's intro post may also be
  // listed with --only or in the activity list).
  if (fetchedThisRun.has(activityUrn)) return readJson(join(ITEMS, `post-${urnId(activityUrn)}.json`));
  fetchedThisRun.add(activityUrn);
  await s.goto(`https://www.linkedin.com/feed/update/${activityUrn}/`, "post");
  await s.scrollGradually(6);
  const html = await s.page.content();
  const p = await s.page.evaluate(() => (window as any).__lf.mainPost());
  // Is this page the post we asked for? (A missing post redirects to /feed/.)
  const landed = s.page.url();
  if (!p) throw new ItemError(`post ${activityUrn}: no post on ${new URL(landed).pathname}`);
  if (!landed.includes(urnId(activityUrn)) || (/:activity:/.test(activityUrn) && p.activity_urn !== activityUrn)) {
    throw new ItemError(`post ${activityUrn}: page shows ${p.activity_urn} at ${new URL(landed).pathname}`);
  }
  // Larger image copies from LinkedIn's image viewer.
  const big = p.media.some((m: any) => m.type === "image") ? await upgradeImages(s, 9) : [];
  const failures: string[] = [];
  const best = bestImageUrls(await s.page.content());
  let imgIdx = 0;
  const media = [];
  for (const m of p.media) {
    if (m.type === "image") {
      // The viewer's larger copy only if it is the same image asset.
      const viewer = big[imgIdx] && assetOf(big[imgIdx]) === assetOf(m.url) ? big[imgIdx] : "";
      const url = viewer || best.get(assetOf(m.url)) || m.url;
      imgIdx++;
      media.push({ ...m, full_url: url, ...(await saveMedia(ctx, url, "post image", failures, m.from + (viewer ? " (larger copy from the image viewer)" : ""))) });
    } else if (m.type === "video") {
      const asset = assetOf(m.poster || "");
      const vtt = asset ? [...s.mediaCache.keys()].find((u) => /webvtt/.test(u) && u.includes(asset)) : undefined;
      media.push({ ...m, poster_file: await saveMedia(ctx, m.poster, "video poster", failures, `${m.from} poster`), captions_file: vtt ? await saveMedia(ctx, vtt, "captions", failures, `captions of video asset ${asset} (from ${m.from})`) : null, download: "not available: LinkedIn streams video as DASH/HLS segments (blob: URL), no single file" });
    } else if (m.type === "link_preview" || m.type === "article") {
      media.push({ ...m, image_file: m.image ? await saveMedia(ctx, best.get(assetOf(m.image)) || m.image, `${m.type} image`, failures, `${m.from} image`) : null });
    } else if (m.type === "document") {
      const pages = [];
      for (const [i, u] of (m.pages || []).entries()) pages.push(await saveMedia(ctx, u, "document page", failures, `${m.from} page ${i + 1}`));
      media.push({ ...m, download_file: m.download ? await saveMedia(ctx, m.download, "document", failures, `${m.from} download link`) : null, page_files: pages });
    } else media.push(m);
  }
  // The quoted post's images (someone else's post, usually), feed size.
  if (p.quote?.images?.length) {
    const files = [];
    for (const [i, u] of p.quote.images.entries()) files.push(await saveMedia(ctx, u, "quoted post image", failures, `quoted post card image #${i + 1}`));
    p.quote.image_files = files;
  }
  const thread = await captureThread(ctx, { kind: "post", activity_urn: activityUrn }, html);
  writeThread(thread);
  // The share id the export uses (urn:li:ugcPost:… or urn:li:share:…).
  // Usually the thread URN; some posts' comments hang off the activity
  // instead, so then look for the ugcPost/share created with the activity.
  let shareUrn = thread?.thread_urn && !/:activity:/.test(thread.thread_urn) ? thread.thread_urn : null;
  if (!shareUrn) {
    const want = idTime(urnId(activityUrn))?.getTime() || 0;
    const cands = [...new Set([...(html + (await s.page.content())).matchAll(/urn:li:(?:ugcPost|share):\d{15,}/g)].map((m) => m[0]))];
    shareUrn = cands.find((u) => Math.abs((idTime(urnId(u))?.getTime() || 0) - want) < 5000) || thread?.thread_urn || null;
  }
  // "Link in comments": Josh's own earliest top-level comment with a link.
  const firstOwn = thread?.comments.find((c: any) => !c.parent_id && c.author.is_self && c.links.length);
  await resolveShortLinks(ctx, p.links);
  // Publish time: the activity's id. (A scheduled post's ugcPost is
  // created when it's scheduled, hours before it goes out.)
  const t = idTime(urnId(/:activity:/.test(activityUrn) ? activityUrn : shareUrn || activityUrn));
  const item = {
    kind: "post",
    fetched_at: iso(new Date()),
    activity_urn: activityUrn,
    share_urn: shareUrn,
    url: `https://www.linkedin.com/feed/update/${shareUrn || activityUrn}/`,
    post_kind: card?.kind === "repost" ? "repost" : p.kind,
    posted_at: iso(t),
    time_text: p.time_text, edited: p.edited,
    author: p.author,
    text: p.text, html: p.html, links: p.links, mentions: p.mentions, hashtags: p.hashtags,
    media, media_types: p.media_types, unknown_components: p.unknown_components,
    quote: p.quote,
    counts: p.counts,
    first_comment_link: firstOwn ? { comment_id: firstOwn.id, url: firstOwn.links[0].url, text: firstOwn.text } : null,
    thread_urn: thread?.thread_urn || shareUrn,
    media_failures: failures,
    missing: p.missing,
  };
  writeJson(join(ITEMS, `post-${urnId(activityUrn)}.json`), item);
  log({ ev: "post", urn: activityUrn, share: shareUrn, kind: item.post_kind, media: p.media_types, unknown: p.unknown_components, media_failed: failures.length, first_comment_link: item.first_comment_link?.url || null });
  return item;
}

// Reposts and announcement posts whose thread we already have: recorded
// from the activity card, no page load.
const listIssues: string[] = [];
const itemName = (c: any) => c.item || `post-${urnId(c.activity_urn)}`;
function recordCard(card: any, extra: Record<string, unknown> = {}) {
  const item = {
    kind: "post", fetched_at: iso(new Date()), from: "activity card",
    activity_urn: card.kind === "repost" && card.repost_of ? null : card.activity_urn, repost_of: card.repost_of || null,
    // ugcPost/share URN (the export's share id) when the card names one.
    share_urn: card.kind !== "repost" && /:(ugcPost|share):/.test(card.post_urn || "") ? card.post_urn : null, url: `https://www.linkedin.com/feed/update/${card.activity_urn}/`, layout: card.layout,
    post_kind: card.kind, posted_at: iso(idTime(urnId(card.activity_urn))), time_text: card.time_text, edited: card.edited,
    author: card.author, text: card.text, html: card.html, links: card.links, mentions: card.mentions, hashtags: card.hashtags,
    media: card.media, media_types: card.media_types, unknown_components: card.unknown_components, quote: card.quote,
    counts: card.counts, first_comment_link: null, thread_urn: null, media_failures: [], missing: card.missing, ...extra,
  };
  writeJson(join(ITEMS, `${itemName(card)}.json`), item);
  log({ ev: "card", urn: card.activity_urn, kind: card.kind, ...extra });
  return item;
}

async function findProfile(ctx: Ctx): Promise<string> {
  if (args.profile) return args.profile.replace(/\/?(\?.*)?$/, "/");
  if (state.profile_url) return state.profile_url;
  const s = ctx.s;
  await s.goto("https://www.linkedin.com/feed/", "me-menu");
  const links = () => s.page.evaluate((sel: string) => [...document.querySelectorAll(sel)].filter((a) => (a as HTMLElement).offsetParent)
    .map((a) => ({ href: (a as HTMLAnchorElement).href.split("?")[0], text: ((a as HTMLElement).innerText || "").trim() })), SEL.meMenuProfileLink[0]);
  const before = new Set((await links()).map((l) => l.href + "|" + l.text));
  let url: string | null = null;
  outer: for (const sel of SEL.expanders.meMenu.sel) {
    for (const b of await s.page.$$(sel)) {
      const t = await b.evaluate((e: Element) => ((e as HTMLElement).innerText || "").trim());
      if (!/^me$/i.test(t)) continue;
      if (!(await s.safeClick(b, "meMenu"))) continue;
      for (let i = 0; i < 15 && !url; i++) {
        await new Promise((r) => setTimeout(r, 300));
        const now = await links();
        const fresh = now.filter((l) => !before.has(l.href + "|" + l.text));
        url = (now.find((l) => /view profile/i.test(l.text)) || fresh[0])?.href || null;
      }
      await s.page.keyboard.press("Escape");
      break outer;
    }
  }
  if (!url) throw new Error("could not read the profile URL from the Me menu (selectors.ts: expanders.meMenu / meMenuProfileLink); pass --profile https://www.linkedin.com/in/<you>/");
  return url.replace(/\/?$/, "/");
}

async function listArticles(ctx: Ctx, profile: string): Promise<string[]> {
  const s = ctx.s;
  await s.goto(`${profile}recent-activity/articles/`, "article-list");
  let links: string[] = [];
  // Newest first. Stop after three articles in a row the blog already has.
  const enough = () => { let run = 0; for (const l of links) { run = knownArticleIds.has(idOf(basenameOf(l))) ? run + 1 : 0; if (run >= 3) return true; } return false; };
  await scrollList(s, async () => {
    links = [...new Set([...links, ...(await s.page.evaluate(() => (window as any).__lf.articleLinks()) as string[])])];
    return enough();
  });
  log({ ev: "article-list", found: links.length });
  return links;
}

// Scroll a profile activity list step by step, calling collect() after
// every step; at the bottom, click "Show more results" (the list stops
// growing without it). Stops when collect() returns true, or when the
// bottom is reached with no button, or after 150 steps.
// First visible element matching an expander's selectors and label.
async function findExpander(s: Session, kind: keyof typeof SEL.expanders) {
  const spec = SEL.expanders[kind];
  for (const sel of spec.sel) {
    for (const e of await s.page.$$(sel)) {
      const ok = await e.evaluate((x: Element, src: string) => !!(x as HTMLElement).offsetParent && new RegExp(src, "i").test(((x as HTMLElement).innerText || "").trim()), spec.label.source);
      if (ok) return e;
    }
  }
  return null;
}

async function scrollList(s: Session, collect: () => Promise<boolean>): Promise<string> {
  let idle = 0;
  let height = 0;
  for (let i = 0; i < 150; i++) {
    if (await collect()) return "reached";
    const st = await s.scrollState();
    if (st.height > height) { height = st.height; idle = 0; }
    if (st.atBottom) {
      if (await collect()) return "reached";
      const more = await findExpander(s, "showMoreResults");
      if (more && (await s.safeClick(more, "showMoreResults"))) { idle = 0; await new Promise((r) => setTimeout(r, 2500)); continue; }
      // No button: the server-driven layout loads more on scroll; give it
      // a few nudges before calling it the end.
      if (++idle >= 4) return "list ended (no Load more, no growth)";
      await new Promise((r) => setTimeout(r, 2500));
      await s.scrollGradually(1);
      continue;
    }
    await s.scrollGradually(1);
  }
  return "step cap (150)";
}

async function listPosts(ctx: Ctx, profile: string, since: Date): Promise<any[]> {
  const s = ctx.s;
  await s.goto(`${profile}recent-activity/all/`, "post-list");
  // The list unloads cards scrolled far past, so collect them as we go.
  const byUrn = new Map<string, any>();
  let cards: any[] = [];
  const oldest = () => Math.min(...cards.map((c) => idTime(urnId(c.activity_urn))?.getTime() || Infinity));
  // Collect after every scroll step: cards are rendered as they come into
  // view and emptied again once far past.
  const collect = async () => {
    for (const c of await s.page.evaluate(() => (window as any).__lf.activityCards())) {
      // The server-driven list layout doesn't show Josh's repost activity,
      // only the original post: key reposts by the original.
      if (!c.activity_urn && c.repost_of) { c.activity_urn = c.repost_of; c.item = `post-repost-${urnId(c.repost_of)}`; }
      if (!c.activity_urn) continue;
      const prev = byUrn.get(c.activity_urn);
      if (!prev || (c.text || "").length + c.media.length > (prev.text || "").length + prev.media.length) byUrn.set(c.activity_urn, c);
    }
    cards = [...byUrn.values()];
    return cards.length > 0 && oldest() < since.getTime();
  };
  const ended = await scrollList(s, collect);
  // The activity page always shows something; finding no cards at all means
  // the page didn't render or the card selector drifted. Fail loudly instead
  // of reporting a clean run with no posts.
  if (!cards.length) throw new Error("post list: no activity cards found (page not rendered, or selectors.ts activityCards drifted). Re-run; if it repeats, fix the selector.");
  const keep = cards.filter((c) => (idTime(urnId(c.activity_urn))?.getTime() || 0) >= since.getTime());
  const oldestSeen = new Date(oldest());
  if (ended !== "reached") listIssues.push(`activity list stopped before --since ${since.toISOString().slice(0, 10)}: oldest card ${oldestSeen.toISOString().slice(0, 10)}, ${cards.length} cards (${ended}). Older posts weren't checked.`);
  log({ ev: "post-list", found: cards.length, ended, oldest: oldestSeen.toISOString().slice(0, 10), since: since.toISOString().slice(0, 10), kept: keep.length, layout: [...new Set(cards.map((c) => c.layout))].join(",") });
  return keep;
}

// ---------------------------------------------------------------------------
// Build: export-shaped files + sidecar from Live/items and Live/threads
// ---------------------------------------------------------------------------
const csvCell = (v: unknown) => { const s = v == null ? "" : String(v); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };

function exportArticleHtml(a: any): string {
  // Same shape as LinkedIn's export: h1 link, p.created, p.published, body.
  let body: string = a.body_html || "";
  // Point each inline image at its largest copy and the sidecar file.
  for (const img of a.images) {
    if (!img.asset) continue;
    const re = new RegExp(`<img([^>]*?)(?:data-li-src|src)="[^"]*${img.asset}[^"]*"([^>]*)>`, "g");
    body = body.replace(re, (_m: string, pre: string, post: string) => {
      const attrs = (pre + post).replace(/\s(src|data-li-src|data-delayed-url|data-live-media)="[^"]*"/g, "");
      return `<img${attrs} src="${(img.source_url || "").replace(/&/g, "&amp;")}"${img.sha256 ? ` data-live-media="${img.file}"` : ""}>`;
    });
  }
  // Native videos: a poster linking to the article (the importer turns the
  // poster into an inline image), then a link.
  let vi = 0;
  // Rendered-body videos (a <figure> holding a <video>) become the stored
  // HTML's placeholder, so both sources go through the same path.
  body = body.replace(/<figure\b[^>]*>(?:(?!<\/figure>)[\s\S])*?<video[\s\S]*?<\/figure>/g, '<div data-type="nativeVideo"></div>');
  body = body.replace(/<div data-type="nativeVideo"><\/div>/g, (m: string) => {
    const v = (a.videos || [])[vi++];
    if (!v?.poster_file) return m;
    const mins = v.duration_s ? ` (${Math.floor(v.duration_s / 60)}:${String(v.duration_s % 60).padStart(2, "0")})` : "";
    return `<p><img src="${v.poster_file.source_url.replace(/&/g, "&amp;")}" data-live-media="${v.poster_file.file}" alt="Video"></p><p><a href="https://www.linkedin.com/pulse/${a.basename}">Watch the video on LinkedIn${mins}</a></p>`;
  });
  body = body.replace(/<!---->/g, "").replace(/\s(id="ember\d+"|data-test-[a-z-]+="[^"]*")/g, "");
  const created = a.created_at ? new Date(a.created_at) : a.published_at ? new Date(a.published_at) : null;
  const published = a.published_at ? new Date(a.published_at) : null;
  const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return [
    "<html><head><meta charset=\"utf-8\"><title>" + esc(a.title) + "</title></head><body>",
    `<h1><a href="https://www.linkedin.com/pulse/${a.basename}">${esc(a.title)}</a></h1>`,
    `<p class="created">Created on ${created ? fmtExport(created) : "---"}</p>`,
    `<p class="published">Published on ${published ? fmtExport(published) : "---"}</p>`,
    `<div>${body}</div>`,
    "</body></html>",
  ].join("\n");
}

function build() {
  const items = readdirSync(ITEMS).filter((f) => f.endsWith(".json")).sort().map((f) => readJson(join(ITEMS, f)));
  const articles = items.filter((i) => i.kind === "article");
  // A repost seen in both list layouts is stored twice (keyed by Josh's
  // repost activity, or by the original post): keep one, preferring the one
  // that names the original.
  const repostKey = (p: any) => `${p.author?.profile_url}|${normText(p.text || "").slice(0, 200)}`;
  const sduiReposts = new Set(items.filter((i) => i.kind === "post" && i.post_kind === "repost" && i.repost_of).map(repostKey));
  const posts = items.filter((i) => i.kind === "post" && !(i.post_kind === "repost" && !i.repost_of && sduiReposts.has(repostKey(i))));
  const threads = existsSync(join(LIVE, "threads")) ? readdirSync(join(LIVE, "threads")).filter((f) => f.endsWith(".json")).sort().map((f) => readJson(join(LIVE, "threads", f))) : [];
  const me = state.profile_url || "";
  // LinkedIn shows no edit date on articles. The best we have: the first
  // fetch whose text differed from the previous fetch's.
  for (const a of articles) {
    const prev = state.articles[a.linkedin_id];
    a.edited_at = prev && prev.hash !== a.text_hash ? a.fetched_at.slice(0, 10) : prev?.edited_at || null;
  }
  const isSelf = (url: string) => !!me && (url || "").replace(/\/$/, "").toLowerCase().endsWith(me.replace(/\/$/, "").split("/in/")[1]?.toLowerCase() || "\u0000");

  // Export files.
  rmSync(join(OUT, "Articles"), { recursive: true, force: true });
  mkdirSync(join(OUT, "Articles", "Articles"), { recursive: true });
  for (const a of articles) writeFileSync(join(OUT, "Articles", "Articles", `${a.basename}.html`), exportArticleHtml(a));
  const shareRows = [["Date", "ShareLink", "ShareCommentary", "SharedUrl", "MediaUrl", "Visibility"]];
  for (const p of posts.filter((p) => p.post_kind !== "repost" && p.share_urn).sort((x, y) => x.posted_at.localeCompare(y.posted_at))) {
    // Like the export: SharedUrl only for external links (empty for a
    // LinkedIn article card), Visibility MEMBER_NETWORK (the export's value
    // on every one of Josh's posts; the page doesn't show it).
    const shared = p.media.find((m: any) => m.type === "link_preview")?.url || "";
    const img = p.media.find((m: any) => m.type === "image");
    const vis = "MEMBER_NETWORK";
    shareRows.push([fmtShareDate(p.activity_urn ? idTime(urnId(p.activity_urn))! : new Date(p.posted_at)), `https://www.linkedin.com/feed/update/${p.share_urn}`, p.text, shared.split("?")[0], img?.source_url || "", vis]);
  }
  writeFileSync(join(OUT, "Shares.csv"), shareRows.map((r) => r.map(csvCell).join(",")).join("\n") + "\n");
  const rm = [["Date/Time", "Media Description", "Media Link"]];
  for (const a of articles.filter((a) => a.cover?.source_url)) {
    const d = new Date(a.published_at || a.created_at);
    const when = d.toLocaleString("en-US", { timeZone: "UTC", month: "long", day: "numeric", year: "numeric" }) + " at " + d.toLocaleString("en-US", { timeZone: "UTC", hour: "numeric", minute: "2-digit", hour12: true });
    rm.push([`You uploaded a article cover photo on ${when}`, a.title, a.cover.source_url]);
  }
  writeFileSync(join(OUT, "Rich_Media.csv"), rm.map((r) => r.map(csvCell).join(",")).join("\n") + "\n");

  // Relations.
  // Ground truth for "which post announced this article": a fetched post
  // page whose comments are the article's thread.
  for (const a of articles) {
    const own = posts.find((p) => p.post_kind !== "repost" && p.from !== "activity card" && p.thread_urn && p.thread_urn === a.thread_urn);
    if (own) { a.intro_activity_urn = own.activity_urn; a.intro_method = "post page shows the article's comment thread"; }
    else if (a.intro_activity_urn) a.intro_method = "article page names the post";
  }
  const rel: any[] = [];
  const articleByBase = new Map(articles.map((a) => [a.basename.toLowerCase(), a]));
  const articleId = (url: string) => idOf(basenameOf(url));
  for (const a of articles) {
    if (a.thread_urn) rel.push({ from: `article:${a.linkedin_id}`, rel: "thread", to: a.thread_urn, method: "comment ids on article page" });
    if (a.intro_activity_urn) rel.push({ from: a.intro_activity_urn, rel: "announces", to: `article:${a.linkedin_id}`, method: a.intro_method });
    const native = findClaim({ title: a.title, basename: a.basename, linkedin_id: a.linkedin_id }, blog);
    if (native) rel.push({ from: `article:${a.linkedin_id}`, rel: "superseded_by", to: `native:${native.slug}`, method: "native_posts claim", path: native.path });
  }
  for (const p of posts) {
    if (p.thread_urn) rel.push({ from: p.activity_urn, rel: "thread", to: p.thread_urn, method: "comment ids on post page" });
    if (p.share_urn) rel.push({ from: p.activity_urn, rel: "same_as", to: p.share_urn, method: "post page" });
    for (const m of p.media.filter((m: any) => m.type === "article" && /\/pulse\//.test(m.url))) {
      const art = articleByBase.get(basenameOf(m.url).toLowerCase());
      const announces = art && art.intro_activity_urn === p.activity_urn;
      if (!announces) rel.push({ from: p.activity_urn, rel: "links_to", to: `article:${articleId(m.url)}`, method: "article card in post", own: /josh-mandel/.test(m.url) || !!art });
    }
    for (const l of p.links) {
      const u = l.resolved || l.url;
      if (/\/pulse\//.test(u)) rel.push({ from: p.activity_urn, rel: "links_to", to: `article:${articleId(u)}`, method: "link in post text" });
      const m = u.match(/linkedin\.com\/(?:feed\/update|posts)\/.*?(urn:li:(?:activity|ugcPost|share):\d+|\d{19})/);
      if (m) rel.push({ from: p.activity_urn, rel: "follows_up", to: m[1].startsWith("urn") ? m[1] : `urn:li:activity:${m[1]}`, method: "link in post text" });
    }
    // A repost card's data-urn is Josh's repost activity; the original's
    // URN isn't on the card, so the original is named by its author.
    // Classic list cards carry Josh's repost activity but not the original;
    // the server-driven layout carries the original (from its componentkey).
    if (p.post_kind === "repost") rel.push({ from: p.activity_urn || `repost-of:${p.repost_of}`, rel: "reposts", to: p.repost_of || null, original_author: p.author?.profile_url || null, own: isSelf(p.author?.profile_url), method: p.repost_of ? "list card componentkey" : "activity card header" });
    if (p.post_kind === "quote" && p.quote) rel.push({ from: p.activity_urn, rel: "quotes", to: p.quote.activity_urn, own: isSelf(p.quote.author?.profile_url), method: "quoted post link" });
    if (p.first_comment_link) {
      const u = p.first_comment_link.url;
      rel.push({ from: p.activity_urn, rel: "first_comment_link", to: /\/pulse\//.test(u) ? `article:${articleId(u)}` : u, url: u, comment_id: p.first_comment_link.comment_id, method: "Josh's first comment" });
    }
  }
  // Which blog page shows which thread: article pages get their own thread
  // and those of posts that announce or link to them; standalone posts get
  // their own. Keys: article:<linkedin_id>, share:<share id>.
  const pages = new Map<string, Set<string>>();
  const add = (urn: string | null, key: string) => { if (!urn) return; if (!pages.has(urn)) pages.set(urn, new Set()); pages.get(urn)!.add(key); };
  for (const a of articles) add(a.thread_urn, `article:${a.linkedin_id}`);
  for (const p of posts) {
    if (p.share_urn) add(p.thread_urn, `share:${urnId(p.share_urn)}`);
    for (const r of rel.filter((r) => r.from === p.activity_urn && (r.rel === "links_to" || r.rel === "announces" || r.rel === "first_comment_link") && String(r.to).startsWith("article:"))) add(p.thread_urn, r.to);
  }
  for (const r of rel.filter((r) => r.rel === "announces")) {
    const p = posts.find((p) => p.activity_urn === r.from);
    if (p?.thread_urn) add(p.thread_urn, r.to);
  }
  for (const t of threads) {
    t.pages = [...(pages.get(t.thread_urn) || [])].sort();
    // The post this thread hangs off: "post announcing the article" vs a later post.
    const announcing = articles.find((a) => a.thread_urn === t.thread_urn);
    t.label = announcing ? "article" : "post";
    writeJson(join(LIVE, "threads", threadKey(t.thread_urn) + ".json"), t);
  }

  const manifest = {
    schema: "linkedin-live/1",
    generated_at: iso(new Date()),
    profile_url: me,
    articles: articles.map(({ body_html, text, ...rest }: any) => rest),
    posts: posts.map(({ html, ...rest }: any) => rest),
    relations: rel,
    threads: Object.fromEntries(threads.map((t) => [t.thread_urn, { file: `Live/threads/${threadKey(t.thread_urn)}.json`, pages: t.pages, displayed: t.displayed, captured: t.captured, complete: t.complete }])),
  };
  writeJson(join(LIVE, "manifest.json"), manifest);

  const zip = join(OUT, "linkedin-live.zip");
  rmSync(zip, { force: true });
  execFileSync("zip", ["-q", "-r", "-X", zip, "Articles", "Shares.csv", "Rich_Media.csv", "Live/manifest.json", "Live/threads", "Live/media"], { cwd: OUT });
  return { articles, posts, threads, rel, zip };
}

// ---------------------------------------------------------------------------
// Checks and report
// ---------------------------------------------------------------------------
function check(built: ReturnType<typeof build>) {
  const out: any[] = [];
  const status = (fails: string[], warns: string[]) => (fails.length ? "FAIL" : warns.length ? "WARN" : "OK");
  const threadOf = (urn: string | null) => built.threads.find((t) => t.thread_urn === urn);
  const threadIssues = (t: any, fails: string[], warns: string[]) => {
    if (!t) return;
    const d = t.displayed.comments, c = t.captured.total;
    if (d != null && c < d) {
      const left = Object.keys(t.expanders_left || {});
      (c < d * 0.8 || left.length ? fails : warns).push(`comments ${c}/${d} captured${left.length ? `; still visible: ${left.join(", ")}` : "; no expanders left (LinkedIn's count may include deleted or hidden comments)"}${t.stuck?.length ? `; stopped: ${t.stuck.join(", ")}` : ""}`);
    }
    if (t.replies_short_on?.length) warns.push(`${t.replies_short_on.length} comment(s) show more replies than captured`);
    const bad = t.comments.filter((x: any) => x.missing?.length);
    if (bad.length) (bad.length > 2 ? fails : warns).push(`${bad.length} comment(s) missing fields: ${[...new Set(bad.flatMap((x: any) => x.missing))].join(", ")}`);
    // Every comment hangs off this thread's post (its id names the post).
    const tid = urnId(t.thread_urn);
    const foreign = t.comments.filter((x: any) => /^urn:li:comment:/.test(x.id) && !x.id.includes(tid));
    if (foreign.length) fails.push(`${foreign.length} comment(s) belong to another post (ids don't name ${t.thread_urn})`);
    for (const x of t.comments) for (const m of x.media || []) if (m.file && !m.from) fails.push(`comment ${x.id}: media without element provenance`);
    if (t.media_failures?.length) warns.push(`${t.media_failures.length} comment media download(s) failed`);
  };
  for (const a of built.articles) {
    const fails: string[] = [], warns: string[] = [];
    if (!a.title) fails.push("no title (selectors.ts: articleTitle)");
    if ((a.text || "").length < 300) fails.push(`article body only ${(a.text || "").length} chars (selectors.ts: articleBody)`);
    if (!a.cover && a.cover_media !== "none" && a.cover_media !== "video (no cover image)") warns.push("no cover image");
    // Provenance: every media file names the element it came from, and the
    // public page agreed on title and cover when the item was fetched.
    for (const m of [a.cover, ...a.images, ...(a.videos || []).flatMap((v: any) => [v.poster_file, v.captions_file])].filter((x: any) => x?.file)) if (!m.from) fails.push(`media ${m.file} has no element provenance`);
    if (!a.public_check) fails.push("no public-page cross-check (fetched before October 2026's fix; re-fetch with --refetch --only)");
    for (const c of a.checks || []) warns.push(c);
    if (!a.created_at) warns.push("no linkedInArticle URN; created date falls back to the publish date");
    if (a.media_failures.length) fails.push(`media downloads failed: ${a.media_failures.join("; ")}`);
    if (a.images.some((i: any) => !i.file)) fails.push("an inline image has no file");
    if (!a.thread_urn) warns.push("comment thread not identified");
    threadIssues(threadOf(a.thread_urn), fails, warns);
    out.push({ item: `article:${a.linkedin_id}`, title: a.title, status: status(fails, warns), fails, warns, comments: threadOf(a.thread_urn)?.captured, displayed: threadOf(a.thread_urn)?.displayed });
  }
  for (const p of built.posts) {
    const fails: string[] = [], warns: string[] = [];
    if (p.missing?.length) fails.push(`post missing ${p.missing.join(", ")}`);
    if (p.from !== "activity card" && p.post_kind !== "repost" && !p.share_urn) fails.push("no ugcPost/share URN (thread not identified)");
    if (p.unknown_components?.length) warns.push(`unknown post components: ${p.unknown_components.join(", ")} (add an extractor in page.ts and selectors.ts)`);
    if (p.media_failures.length) fails.push(`media downloads failed: ${p.media_failures.join("; ")}`);
    const files = (p.media || []).flatMap((m: any) => [m.file ? m : null, m.poster_file, m.captions_file, m.image_file, m.download_file, ...(m.page_files || [])]).concat(p.quote?.image_files || []).filter((x: any) => x?.file);
    for (const m of files) if (!m.from) fails.push(`media ${m.file} has no element provenance`);
    if (p.post_kind === "quote" && !p.quote?.activity_urn) warns.push("quoted post's URN not found");
    if (p.post_kind !== "repost") for (const l of p.links.filter((l: any) => /lnkd\.in/.test(l.url) && !l.resolved)) warns.push(`unresolved short link ${l.url}`);
    threadIssues(threadOf(p.thread_urn), fails, warns);
    out.push({ item: p.activity_urn || `repost-of:${p.repost_of}`, kind: p.post_kind, text: (p.text || "").slice(0, 60), status: status(fails, warns), fails, warns, comments: threadOf(p.thread_urn)?.captured, displayed: threadOf(p.thread_urn)?.displayed });
  }
  return out;
}

function changes(built: ReturnType<typeof build>) {
  const res: any[] = [];
  for (const a of built.articles) {
    const prev = state.articles[a.linkedin_id];
    const native = findClaim({ title: a.title, basename: a.basename, linkedin_id: a.linkedin_id }, blog);
    const imported = blog.find((e) => e.kind === "linkedin" && (e.linkedin_id === a.linkedin_id || basenameOf(e.original_url || "") === a.basename));
    const entry: any = { article: a.linkedin_id, title: a.title };
    if (prev && prev.hash !== a.text_hash) entry.changed_since_last_fetch = prev.fetched_at;
    // Captions are left out: LinkedIn caps them at 250 characters, so native
    // posts keep longer ones on purpose (AGENTS.md).
    const captions = new Set(a.images.map((i: any) => (i.caption || "").trim()).filter(Boolean));
    const text = a.text.split("\n").filter((l: string) => !captions.has(l.trim())).join("\n");
    if (native) {
      const missing = missingBlocks(text, native.body);
      entry.native = native.path;
      if (missing.length) entry.linkedin_paragraphs_not_in_native = missing;
    } else if (imported) {
      const missing = missingBlocks(text, imported.body);
      if (missing.length) entry.linkedin_paragraphs_not_in_blog = missing.length;
    } else entry.new = true;
    res.push(entry);
    state.articles[a.linkedin_id] = { hash: a.text_hash, title: a.title, fetched_at: a.fetched_at, url: a.url, edited_at: a.edited_at || null };
  }
  return res;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
// --extract-file <saved.html>: run the in-page extractors on a saved page
// (e.g. Live/error-page.html) in a tab with all network requests blocked.
// No LinkedIn load; for checking a selector fix offline.
async function extractFile(file: string) {
  const session = new Session({ cdpUrl: args["cdp-url"]!, maxPages: 0, minDelayMs: 0, maxDelayMs: 0, log });
  await session.open();
  try {
    const page = session.page;
    await page.setRequestInterception(true);
    page.on("request", (r) => (r.url() === "about:blank" || r.url().startsWith("data:") ? r.continue() : r.abort()));
    await page.setJavaScriptEnabled(false);
    await page.setContent(readFileSync(file, "utf8").replace(/<script[\s\S]*?<\/script>/g, ""), { waitUntil: "domcontentloaded" });
    await page.setJavaScriptEnabled(true);
    await session.installHelpers();
    const out = await page.evaluate(() => {
      const lf = (window as any).__lf;
      return { activityCards: lf.activityCards(), articleLinks: lf.articleLinks(), comments: lf.comments(""), threadCounts: lf.threadCounts(), article: (() => { const a = lf.article(); return { ...a, body_html: `${a.body_html.length} chars`, body_text: `${a.body_text.length} chars` }; })(), expanders: lf.expanders() };
    });
    console.log(JSON.stringify(out, null, 1));
  } finally { await session.close(); }
  return 0;
}

// Probe the activity list: the first screenful of cards must parse, with
// URNs, authors, time and text or media, in either list layout.
async function probeList(ctx: Ctx, profile: string) {
  const s = ctx.s;
  await s.goto(`${profile}recent-activity/all/`, "post-list");
  await s.scrollGradually(4);
  const cards: any[] = await s.page.evaluate(() => (window as any).__lf.activityCards());
  const fails: string[] = [], warns: string[] = [];
  if (cards.length < 3) fails.push(`only ${cards.length} activity cards (selectors.ts: activityCard / sdui.card)`);
  const bad = cards.filter((c) => c.missing?.length);
  if (bad.length) fails.push(`${bad.length} card(s) missing ${[...new Set(bad.flatMap((c) => c.missing))].join(", ")}`);
  if (!cards.some((c) => c.kind !== "repost" && (c.activity_urn || c.post_urn))) fails.push("no original post with a URN");
  if (cards.some((c) => !c.author?.name)) warns.push("card(s) with no author name");
  if (cards.some((c) => c.unknown_components?.length)) warns.push(`unknown components: ${[...new Set(cards.flatMap((c) => c.unknown_components))].join(", ")}`);
  const layout = [...new Set(cards.map((c) => c.layout))].join(",");
  log({ ev: "probe-list", cards: cards.length, layout, kinds: cards.map((c) => c.kind).join(",") });
  return { item: "probe:post-list", title: `activity list (${layout || "no cards"}, ${cards.length} cards)`, status: fails.length ? "FAIL" : warns.length ? "WARN" : "OK", fails, warns };
}

// --capture-video <post url>: save a LinkedIn video as an MP4 in
// linkedin_work/video/<activity id>.mp4 (gitignored), for Josh to upload to
// YouTube. One paced page load per video; read-only. Prefers the
// progressive MP4 named in the page's embedded data (highest bitrate);
// falls back to ffmpeg on the DASH/HLS manifest the player requests.
async function captureVideos(urls: string[]) {
  const outDir = join(BLOG, "linkedin_work", "video");
  mkdirSync(outDir, { recursive: true });
  const session = new Session({ cdpUrl: args["cdp-url"]!, maxPages: Number(args["max-pages"]), minDelayMs: Number(args["min-delay"]), maxDelayMs: Number(args["max-delay"]), log });
  await session.open();
  let failed = 0;
  try {
    for (const u of urls) {
      const urn = u.match(/urn:li:(activity|ugcPost|share):\d+/)?.[0];
      if (!urn) throw new Error(`not a post URL: ${u}`);
      const manifests: string[] = [];
      const onResp = (r: any) => { const t = r.headers()["content-type"] || ""; if (/dash\+xml|mpegurl/i.test(t)) manifests.push(r.url()); };
      session.page.on("response", onResp);
      await session.goto(`https://www.linkedin.com/feed/update/${urn}/`, "video");
      await session.scrollGradually(2);
      await new Promise((r) => setTimeout(r, 3000));
      session.page.off("response", onResp);
      const streams: any[] = await session.page.evaluate(() => {
        const out: any[] = [];
        const walk = (o: any) => {
          if (!o || typeof o !== "object") return;
          if (Array.isArray(o.progressiveStreams)) for (const p of o.progressiveStreams) for (const l of p.streamingLocations || []) if (l.url) out.push({ url: l.url, bitRate: p.bitRate || 0, width: p.width, height: p.height, size: p.size, type: p.mediaType });
          for (const v of Object.values(o)) walk(v);
        };
        for (const c of document.querySelectorAll("code")) { try { walk(JSON.parse(c.textContent || "")); } catch { /* not JSON */ } }
        return out;
      });
      const item = readJson(join(ITEMS, `post-${urnId(urn)}.json`));
      const want = item?.media?.find((m: any) => m.type === "video")?.duration_s ?? null;
      const out = join(outDir, `${urnId(urn)}.mp4`);
      const best = streams.filter((x) => /mp4/.test(x.type || "mp4")).sort((a, b) => b.bitRate - a.bitRate)[0];
      let how = "";
      try {
        if (best) {
          execFileSync("ffmpeg", ["-v", "error", "-y", "-i", best.url, "-c", "copy", "-movflags", "+faststart", out], { stdio: "inherit", timeout: 20 * 60_000 });
          how = `progressive MP4 ${best.width}x${best.height} @ ${Math.round(best.bitRate / 1000)} kb/s`;
        } else if (manifests.length) {
          execFileSync("ffmpeg", ["-v", "error", "-y", "-i", manifests[0], "-c", "copy", "-movflags", "+faststart", out], { stdio: "inherit", timeout: 20 * 60_000 });
          how = "ffmpeg from the stream manifest";
        } else throw new Error("no progressive stream or manifest found on the page");
        const dur = Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).toString().trim());
        const size = (await import("node:fs")).statSync(out).size;
        const ok = want == null || Math.abs(dur - want) <= 3;
        log({ ev: "video", urn, file: out, mb: +(size / 1e6).toFixed(1), duration_s: Math.round(dur), expected_s: want, how, ok });
        if (!ok) failed++;
      } catch (e) {
        failed++;
        log({ ev: "video-failed", urn, error: String((e as Error).message).slice(0, 300), streams: streams.length, manifests: manifests.length });
      }
    }
  } finally { await session.close(); }
  return failed ? 2 : 0;
}

async function main() {
  if (args["extract-file"]) return extractFile(args["extract-file"]);
  if (args["capture-video"]!.length) return captureVideos(args["capture-video"]!);
  const doArticles = args.articles || (!args.posts && !args.only!.length && !args.probe);
  const doPosts = args.posts || (!args.articles && !args.only!.length && !args.probe);
  let exitCode = 0;
  const probeItems: any[] = [];
  const session = new Session({ cdpUrl: args["cdp-url"]!, maxPages: Number(args["max-pages"]), minDelayMs: Number(args["min-delay"]), maxDelayMs: Number(args["max-delay"]), log });
  if (!args["build-only"]) {
    await session.open();
    const ctx: Ctx = { s: session, me: "", report: [] };
    try {
      const profile = await findProfile(ctx);
      state.profile_url = profile;
      ctx.me = profile.split("/in/")[1].replace(/\/$/, "");
      log({ ev: "profile", url: profile });
      const done = (f: string) => !args.refetch && existsSync(join(ITEMS, f));
      const only = args.probe ? [PROBE_PAGES.article, PROBE_PAGES.post] : args.only!;
      if (args.probe) probeItems.push(await probeList(ctx, profile));
      const fetchedArticles: any[] = [];
      for (const u of only) {
        if (/\/pulse\//.test(u)) {
          const f = `article-${idOf(basenameOf(u))}.json`;
          fetchedArticles.push(!done(f) || args.probe || args.refetch ? await guarded(`article:${idOf(basenameOf(u))}`, () => fetchArticle(ctx, u)) : readJson(join(ITEMS, f)));
        }
        else {
          const urn = u.match(/urn:li:(activity|ugcPost|share):\d+/)?.[0];
          if (!urn) throw new Error(`not a post or article URL: ${u}`);
          if (!done(`post-${urnId(urn)}.json`) || args.probe || args.refetch) await guarded(urn, () => fetchPost(ctx, urn, null));
        }
      }
      // The post announcing each fetched article: its text is the article's
      // intro on the blog. (The activity list covers this in --posts runs.)
      if (!doPosts) {
        for (const a of fetchedArticles) {
          if (a && a.intro_activity_urn && (!done(`post-${urnId(a.intro_activity_urn)}.json`) || args.probe || args.refetch)) await guarded(a.intro_activity_urn, () => fetchPost(ctx, a.intro_activity_urn, null));
        }
      }
      if (doArticles) {
        const links = await listArticles(ctx, profile);
        const want = links.filter((l) => !knownArticleIds.has(idOf(basenameOf(l))) || args.refetch);
        log({ ev: "plan", articles: want.length, skipped_known: links.length - want.length });
        if (args["dry-run"]) console.log("Would fetch articles:\n  " + want.join("\n  "));
        else for (const l of want) if (!done(`article-${idOf(basenameOf(l))}.json`)) fetchedArticles.push(await guarded(`article:${idOf(basenameOf(l))}`, () => fetchArticle(ctx, l)));
      }
      if (doPosts) {
        const newest = shareDates.length ? new Date(shareDates[shareDates.length - 1] + (shareDates[shareDates.length - 1].endsWith("Z") ? "" : "Z")) : new Date(Date.now() - 30 * 86400_000);
        const since = args.since ? new Date(args.since) : new Date(newest.getTime() - 3 * 86400_000);
        const cards = await listPosts(ctx, profile, since);
        const arts = readdirSync(ITEMS).filter((f) => f.startsWith("article-")).map((f) => readJson(join(ITEMS, f)));
        const articleThreads = new Map(cards.filter((c) => c.kind !== "repost").map((c) => [c.activity_urn, arts.find((a) => a.intro_activity_urn === c.activity_urn || (c.post_urn && c.post_urn === a.thread_urn) || sameTime(c.activity_urn, a.thread_urn))]).filter(([, a]) => a) as [string, any][]);
        const plan = cards.map((c) => ({ c, how: c.kind === "repost" ? "card (repost)" : articleThreads.has(c.activity_urn) ? "card (thread captured with its article)" : "post page" }));
        log({ ev: "plan", posts: plan.length, pages: plan.filter((p) => p.how === "post page").length });
        if (args["dry-run"]) console.log("Would fetch posts:\n  " + plan.map((p) => `${p.c.activity_urn} ${p.c.kind} via ${p.how}: ${p.c.text.slice(0, 60)}`).join("\n  "));
        else for (const { c, how } of plan) {
          if (done(`${itemName(c)}.json`)) continue;
          if (how === "post page") await guarded(c.activity_urn, () => fetchPost(ctx, c.activity_urn, c));
          else {
            const a = articleThreads.get(c.activity_urn);
            recordCard(c, a ? { share_urn: a.thread_urn, thread_urn: a.thread_urn, url: `https://www.linkedin.com/feed/update/${a.thread_urn}/` } : {});
          }
        }
      }
    } catch (e) {
      if (e instanceof Blocked) { console.error(`\nSTOP: ${e.message}`); exitCode = 3; }
      else if (e instanceof BudgetExceeded) { console.error(`\nSTOP: ${e.message}. Re-run to continue; fetched items are kept.`); exitCode = 4; }
      else { console.error(`\nERROR: ${(e as Error).stack}`); exitCode = 1; }
      try { writeFileSync(join(LIVE, "error-page.html"), await session.page.content()); await session.page.screenshot({ path: join(LIVE, "error-page.png") }); } catch { /* page gone */ }
    } finally {
      await session.close();
    }
  }
  if (args["dry-run"]) { console.log(`\nDry run: ${session.pageLoads} page loads, nothing written.`); return exitCode; }
  if (!readdirSync(ITEMS).length) { console.error("Nothing fetched; no output built."); return exitCode || 1; }

  const built = build();
  const items = [...probeItems, ...itemFailures, ...listIssues.map((w) => ({ item: "post-list", title: "activity list", status: "WARN", fails: [], warns: [w] })), ...check(built)];
  const changed = changes(built);
  writeJson(STATE_FILE, state);
  const summary = { OK: 0, WARN: 0, FAIL: 0 } as Record<string, number>;
  for (const i of items) summary[i.status]++;
  const report = {
    generated_at: iso(new Date()),
    page_loads: session.pageLoads, clicks: session.clicks,
    summary, items, changes: changed,
    relations: built.rel.length, zip: built.zip,
  };
  writeJson(join(LIVE, "report.json"), report);
  console.log(`\n=== LinkedIn live fetch: ${session.pageLoads} page loads, ${session.clicks} clicks ===`);
  for (const i of items) {
    const c = i.comments ? ` comments ${i.comments.total}/${i.displayed?.comments ?? "?"}` : "";
    console.log(`${i.status.padEnd(4)} ${i.item} ${(i.title || i.kind || "").slice(0, 50)}${c}`);
    for (const f of i.fails) console.log(`       FAIL ${f}`);
    for (const w of i.warns) console.log(`       warn ${w}`);
  }
  for (const c of changed) {
    if (c.changed_since_last_fetch) console.log(`CHANGED on LinkedIn since ${c.changed_since_last_fetch}: ${c.title}`);
    if (c.linkedin_paragraphs_not_in_native) console.log(`BACKPORT? ${c.title} → ${c.native}: ${c.linkedin_paragraphs_not_in_native.length} LinkedIn paragraph(s) not in the native post, e.g. "${c.linkedin_paragraphs_not_in_native[0]}"`);
  }
  console.log(`\n${summary.OK} OK, ${summary.WARN} WARN, ${summary.FAIL} FAIL. Report: ${join(LIVE, "report.json")}\nImport with: ./scripts/local-import.sh ${built.zip}`);
  if (!exitCode && summary.FAIL) exitCode = 2;
  return exitCode;
}

process.exit(await main());
