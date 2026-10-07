#!/usr/bin/env python3
"""Audit LinkedIn-derived blog content against LinkedIn's public pages.

Run before every commit that touches imported content (AGENTS.md runbook).
Exit code 1 if anything FAILs.

    .venv-import/bin/python scripts/linkedin_audit.py            # full audit
    .venv-import/bin/python scripts/linkedin_audit.py --offline  # repo/dist checks only
    .venv-import/bin/python scripts/linkedin_audit.py --only d22wc --refresh

Every check compares the blog with an independent source. Public pages are
fetched logged out with plain HTTP (no cookies), paced 3-6 s, and cached in
linkedin_work/audit/cache for --max-age-hours (default 168). Media
downloads (images only) are cached by URL.

Articles (imported, and native posts that name a LinkedIn original):
  - the public page is the article (final URL has the same 5-char id);
  - title (imported: must match; native: not checked), slug, publish date;
  - body: the first paragraphs of the blog copy appear on the public page;
  - cover: the banner is visually the public page's own cover
    (figure.cover-img / JSON-LD image), and there is no banner when LinkedIn
    has no cover. Never compared with other images on the page: its body
    and sidebars carry other articles' covers;
  - inline images: each is visually one of the article's own inline images
    (inside the body, outside embedded cards of other articles).
Posts (shares with media, and every post placed on an article page):
  - the public post page is that post; its images / video poster match;
  - intro_share and also_posted posts really carry that article's link.
Threads: comment ids name the thread's post; no comment in two threads;
  captured vs displayed counts; pages resolve; one name per profile;
  comments shown on the public post page appear in the thread.
Links (built site, dist/): every internal link and image resolves; every
  LinkedIn URL in content maps (linkmap.mjs) to the page with that id.
YouTube registry: each id exists (oEmbed) and fits the post or article.
Live items (linkedin_work/live): every media file names its element.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import random
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from PIL import Image
from slugify import slugify

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
BLOG = pathlib.Path("src/content/blog")
SHARES = pathlib.Path("src/content/shares/linkedin")
THREADS = pathlib.Path("src/data/linkedin/threads")
YOUTUBE = pathlib.Path("src/data/youtube.json")
WORK = pathlib.Path("linkedin_work/audit")
CACHE = WORK / "cache"
HASH_MAX_DIST = 12  # of 64 bits (dHash); same image re-encoded/resized: 0-6
ME = "/in/josh-mandel"

findings: List[dict] = []


def add(sev: str, cat: str, subject: str, msg: str) -> None:
    findings.append({"severity": sev, "category": cat, "subject": subject, "message": msg})


# ---------------------------------------------------------------------------
# Fetching (cached, paced)
# ---------------------------------------------------------------------------
class Fetcher:
    def __init__(self, offline: bool, refresh: bool, max_age_h: float, max_fetch: int) -> None:
        self.offline, self.refresh, self.max_age, self.max_fetch = offline, refresh, max_age_h * 3600, max_fetch
        self.fetched = 0
        self.last = 0.0
        self.s = requests.Session()
        self.s.headers.update({"user-agent": UA, "accept-language": "en-US,en"})
        CACHE.mkdir(parents=True, exist_ok=True)

    def _path(self, url: str, ext: str) -> pathlib.Path:
        return CACHE / (hashlib.sha256(url.encode()).hexdigest()[:24] + ext)

    def page(self, url: str) -> Optional[dict]:
        """A LinkedIn page, logged out: {status, final_url, html} or None."""
        p = self._path(url, ".json")
        if p.exists() and not self.refresh and time.time() - p.stat().st_mtime < self.max_age:
            return json.loads(p.read_text(encoding="utf-8"))
        if self.offline:
            return None
        if self.fetched >= self.max_fetch:
            add("WARN", "audit", url, f"not checked: --max-fetch {self.max_fetch} reached (re-run to continue; results are cached)")
            return None
        wait = self.last + random.uniform(3.0, 6.0) - time.time()
        if wait > 0:
            time.sleep(wait)
        self.fetched += 1
        self.last = time.time()
        try:
            r = self.s.get(url, timeout=40, allow_redirects=True)
            out = {"status": r.status_code, "final_url": r.url, "html": r.text, "fetched_at": datetime.now(timezone.utc).isoformat()}
        except Exception as exc:
            add("WARN", "audit", url, f"fetch failed: {exc}")
            return None
        if r.status_code == 429 or "authwall" in r.url or "/checkpoint/" in r.url:
            add("FAIL", "audit", url, f"LinkedIn refused the public fetch ({r.status_code} {r.url}); stop and wait")
            raise SystemExit(2)
        p.write_text(json.dumps(out), encoding="utf-8")
        print(f"  [fetch {self.fetched}] {r.status_code} {url}")
        return out

    def media(self, url: str) -> Optional[bytes]:
        p = self._path(url, ".bin")
        if p.exists():
            return p.read_bytes()
        if self.offline:
            return None
        time.sleep(0.3)
        try:
            r = self.s.get(url, timeout=40)
            if r.status_code != 200:
                return None
            p.write_bytes(r.content)
            return r.content
        except Exception:
            return None


def dhash(data: bytes) -> Optional[int]:
    try:
        im = Image.open(io.BytesIO(data))
        im.seek(0)
        im = im.convert("L").resize((9, 8), Image.LANCZOS)
    except Exception:
        return None
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
    return bits


def dist(a: Optional[int], b: Optional[int]) -> int:
    return 64 if a is None or b is None else bin(a ^ b).count("1")


# ---------------------------------------------------------------------------
# Repo content
# ---------------------------------------------------------------------------
def frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"---\n(.*?)\n---\n?", text, re.DOTALL)
    return (m.group(1), text[m.end():]) if m else ("", text)


def scalar(fm: str, key: str) -> Optional[str]:
    m = re.search(rf"^{key}:[ \t]*(.*?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") or None if m else None


def nested_ids(fm: str, block: str) -> List[str]:
    m = re.search(rf"^{block}:\n((?:[ \t-].*\n?)*)", fm + "\n", re.MULTILINE)
    return re.findall(r"share_id:[ \t]*\"?(\d+)", m.group(1)) if m else []


def pulse_id(url: Optional[str]) -> Optional[str]:
    m = re.search(r"linkedin\.com/pulse/[^?#\"'\s]*-([a-z0-9]{5})/?(?:[?#\"'\s]|$)", url or "")
    return m.group(1) if m else None


def load_posts() -> List[dict]:
    posts = []
    for p in sorted(BLOG.rglob("index.md")):
        fm, body = frontmatter(p.read_text(encoding="utf-8"))
        claims = re.findall(r"linkedin\.com/pulse/[^\"'\s]+", fm)
        posts.append({
            "path": p, "dir": p.parent, "native": "linkedin" not in p.relative_to(BLOG).parts[:1],
            "title": scalar(fm, "title") or "", "slug": scalar(fm, "slug") or p.parent.name, "date": scalar(fm, "date"),
            "original_url": scalar(fm, "original_url"), "linkedin_id": scalar(fm, "linkedin_id"),
            "banner": scalar(fm, "banner"), "claims": claims, "draft": scalar(fm, "draft") == "true",
            "intro": nested_ids(fm, "intro_share"), "also": nested_ids(fm, "also_posted"), "fm": fm, "body": body,
        })
    return posts


def load_shares() -> List[dict]:
    out = []
    for p in sorted(SHARES.glob("*/index.md")):
        fm, body = frontmatter(p.read_text(encoding="utf-8"))
        out.append({"path": p, "dir": p.parent, "id": scalar(fm, "share_id"), "url": scalar(fm, "share_url"),
                    "date": scalar(fm, "date"), "title": scalar(fm, "title") or "", "fm": fm, "body": body})
    return out


def plain(md: str) -> str:
    t = re.sub(r"<(style|script|svg)[\s\S]*?</\1>", " ", md)
    t = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", t, flags=re.MULTILINE)  # list markers (LinkedIn's are CSS)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[*_`>#|\\]", " ", t)
    return t


def norm(t: str) -> str:
    t = (t or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def local_images(post_dir: pathlib.Path, body: str) -> List[pathlib.Path]:
    names = re.findall(r"!\[[^\]]*\]\(\./([^)\s]+)\)", body) + re.findall(r"<img[^>]*src=\"\./([^\"]+)\"", body)
    seen, out = set(), []
    for n in names:
        if n not in seen and (post_dir / n).exists():
            seen.add(n)
            out.append(post_dir / n)
    return out


# ---------------------------------------------------------------------------
# Public page parsing
# ---------------------------------------------------------------------------
def parse_article(html: str) -> dict:
    s = BeautifulSoup(html, "html.parser")
    meta = lambda p: (s.find("meta", attrs={"property": p}) or s.find("meta", attrs={"name": p}) or {}).get("content")
    ld = {}
    for sc in s.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(sc.get_text())
            if d.get("@type") == "Article":
                ld = d
        except Exception:
            pass
    fig = s.select_one("figure.cover-img img")
    cover = (fig.get("data-delayed-url") or fig.get("src")) if fig else None
    cover = cover or (ld.get("image") or {}).get("url")
    og = meta("og:image") or ""
    if not cover and "article-cover_image" in og:
        cover = og
    body = s.select_one('[data-test-id="article-content-blocks"]')
    inline, videos = [], []
    if body:
        for card in body.select(".inline-articles, .content-author-card"):
            card.decompose()  # cards of other articles
        for img in body.find_all("img"):
            u = img.get("data-delayed-url") or img.get("src") or ""
            if "article-inline_image" in u:
                inline.append(u)
            elif re.search(r"videocover|playlist/vid", u):
                videos.append(u)
        for v in body.find_all("video"):  # native video: <video data-poster-url>
            if v.get("data-poster-url"):
                videos.append(v["data-poster-url"])
    return {"title": ld.get("name") or meta("og:title"), "date_published": ld.get("datePublished"),
            "comment_count": int(ld["commentCount"]) if str(ld.get("commentCount", "")).isdigit() else None,
            "cover": cover, "og_image": og, "inline": inline, "videos": videos, "text": norm(body.get_text(" ") if body else s.get_text(" "))}


def parse_post(html: str) -> dict:
    s = BeautifulSoup(html, "html.parser")
    meta = lambda p: (s.find("meta", attrs={"property": p}) or {}).get("content")
    ld = {}
    for sc in s.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(sc.get_text())
            if d.get("@type") in ("SocialMediaPosting", "VideoObject", "Article", "DiscussionForumPosting"):
                ld = d
        except Exception:
            pass
    main = s.select_one("article") or s
    imgs = []
    for img in main.find_all("img"):
        u = img.get("data-delayed-url") or img.get("src") or ""
        if re.search(r"feedshare|articleshare|article-cover_image|/sync/", u):
            imgs.append(u)
    comments = [c.get("text", "") for c in ld.get("comment", []) if isinstance(c, dict)]
    return {"og_url": meta("og:url") or "", "date_published": ld.get("datePublished"), "thumbnail": ld.get("thumbnailUrl"),
            "images": imgs, "comments": comments, "html": html, "text": norm(main.get_text(" ")),
            "description": meta("og:description") or ""}


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check_articles(posts, F: Fetcher, only: Optional[str]) -> Dict[str, dict]:
    pages: Dict[str, dict] = {}
    for p in posts:
        lid = p["linkedin_id"] or pulse_id(p["original_url"])
        if not lid or (only and lid != only) or p["draft"]:
            continue
        subj = f"{'native' if p['native'] else 'article'} {p['slug']} ({lid})"
        url = p["original_url"] or next((c for c in p["claims"] if pulse_id(c) == lid), None)
        page = F.page(url.split("?")[0].rstrip("/")) if url else None
        if not page:
            continue
        if "article_not_found" in page["final_url"] or re.search(r"/(signup|login|authwall)", page["final_url"]):
            add("WARN", "article", subj, f"not publicly visible ({page['final_url'][:70]}); can't verify logged out")
            continue
        if page["status"] != 200 or pulse_id(page["final_url"] + " ") != lid:
            add("FAIL", "article", subj, f"public page {page['status']} at {page['final_url']}")
            continue
        a = parse_article(page["html"])
        pages[lid] = a
        # Title, slug, date
        if not p["native"]:
            if norm(a["title"]) != norm(p["title"]):
                ratio = SequenceMatcher(None, norm(a["title"]), norm(p["title"])).ratio()
                add("FAIL" if ratio < 0.6 else "WARN", "article", subj, f"title \"{p['title']}\" vs LinkedIn \"{a['title']}\"")
            if p["slug"] != slugify(p["title"], lowercase=True):
                add("WARN", "article", subj, f"slug {p['slug']} isn't the slug of its title")
        if a["date_published"] and p["date"] and not p["native"]:
            pub = datetime.fromisoformat(a["date_published"].replace("Z", "+00:00"))
            loc = datetime.fromisoformat(p["date"][:19]).replace(tzinfo=timezone.utc)
            if (loc - pub).total_seconds() > 86400:
                add("FAIL", "article", subj, f"date {p['date']} is after LinkedIn's publish date {a['date_published']}")
            elif (pub - loc).days > 120:
                add("WARN", "article", subj, f"date {p['date']} is {(pub - loc).days} days before publication ({a['date_published']})")
        # Body: first paragraphs appear on the public page
        if not p["native"]:
            paras = [norm(x) for x in re.split(r"\n\s*\n", plain(p["body"])) if len(norm(x)) > 60][:3]
            hits = sum(1 for x in paras if x[:80] in a["text"])
            if paras and hits == 0:
                add("FAIL", "article", subj, "none of the first paragraphs appear on the public page (wrong article body?)")
            elif paras and hits < len(paras):
                add("WARN", "article", subj, f"{len(paras) - hits} of the first {len(paras)} paragraphs differ from the public page (edited?)")
            # Completeness: words LinkedIn shows that the blog copy lacks
            # (LinkedIn's stored HTML, and so the export, can drop code).
            from collections import Counter
            ours = Counter(re.findall(r"[a-z0-9]+", norm(plain(p["body"]) + " " + p["body"])))
            theirs = Counter(re.findall(r"[a-z0-9]+", a["text"]))
            missing = theirs - ours
            n_missing = sum(missing.values())
            if n_missing > max(25, 0.02 * sum(theirs.values())):
                add("FAIL", "article", subj, f"the blog copy lacks {n_missing} of the {sum(theirs.values())} words LinkedIn shows (e.g. {', '.join(w for w, _ in missing.most_common(8))}); re-fetch it")
        # Cover
        banner = None
        if p["banner"] and p["banner"].startswith("./"):
            banner = p["dir"] / p["banner"][2:]
        elif not p["native"]:
            banner = next((p["dir"] / f"banner{e}" for e in (".png", ".jpg", ".jpeg", ".gif", ".webp") if (p["dir"] / f"banner{e}").exists()), None)
        if a["cover"]:
            if not banner or not banner.exists():
                add("WARN", "cover", subj, "LinkedIn has a cover; the blog has no banner")
            else:
                pub = F.media(a["cover"])
                d = dist(dhash(banner.read_bytes()), dhash(pub)) if pub else None
                if d is None:
                    add("WARN", "cover", subj, "couldn't download the public cover to compare")
                elif d > HASH_MAX_DIST:
                    add("FAIL", "cover", subj, f"{banner.name} is not this article's LinkedIn cover (hash distance {d})")
        elif banner and banner.exists():
            kind = "video thumbnail" if "playlist/vid" in a["og_image"] else "no cover"
            add("WARN" if p["native"] else "FAIL", "cover", subj, f"{banner.name} present, but LinkedIn has no cover ({kind})")
        # Inline images (imported articles only; native posts have their own figures)
        if not p["native"]:
            pub_hashes = []
            for u in a["inline"]:
                data = F.media(u)
                pub_hashes.append(dhash(data) if data else None)
            posters = set(re.findall(r"!\[Video\]\(\./([^)\s]+)\)", p["body"]))
            vid_hashes = [dhash(d) for d in (F.media(u) for u in a["videos"]) if d]
            for name in posters:
                best = min((dist(dhash((p["dir"] / name).read_bytes()), h) for h in vid_hashes), default=64) if (p["dir"] / name).exists() else 64
                if best > HASH_MAX_DIST:
                    add("FAIL", "image", subj, f"video poster {name} doesn't match the article's videos on LinkedIn ({len(vid_hashes)} found, distance {best})")
            body_imgs = [x for x in local_images(p["dir"], p["body"]) if x.suffix.lower() != ".svg" and x.name not in posters]
            for img in body_imgs:
                h = dhash(img.read_bytes())
                best = min((dist(h, ph) for ph in pub_hashes), default=64)
                if best > HASH_MAX_DIST:
                    is_banner = img.name.startswith("banner")
                    if is_banner and a["cover"]:
                        continue  # the cover shown in the body too; checked above
                    add("FAIL", "image", subj, f"{img.name} doesn't match any of the article's {len(pub_hashes)} inline images on LinkedIn (distance {best})")
            if len(body_imgs) < len(a["inline"]):
                add("WARN", "image", subj, f"{len(a['inline'])} inline images on LinkedIn, {len(body_imgs)} on the blog")
    return pages


def check_posts(posts, shares, F: Fetcher, threads, only: Optional[str]) -> None:
    by_lid = {}
    for p in posts:
        lid = p["linkedin_id"] or pulse_id(p["original_url"])
        if lid:
            by_lid.setdefault(lid, p)
    targets = []  # (share id, why, article post or None, share entry or None)
    for p in posts:
        lid = p["linkedin_id"] or pulse_id(p["original_url"])
        if only and lid != only:
            continue
        for sid in p["intro"]:
            targets.append((sid, "intro_share", p, None))
        for sid in p["also"]:
            targets.append((sid, "also_posted", p, None))
    for sh in shares:
        files = [f for f in sh["dir"].iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")]
        if files and not only:
            targets.append((sh["id"], "share media", None, sh))
    seen = set()
    for sid, why, art, sh in targets:
        if (sid, why) in seen:
            continue
        seen.add((sid, why))
        types = ["ugcPost", "share"] if not sh else [re.search(r"urn:li:(\w+):", sh["url"] or "urn:li:ugcPost:").group(1)]
        page = None
        for t in types:  # an id from Shares.csv may be a ugcPost or a share
            page = F.page(f"https://www.linkedin.com/feed/update/urn:li:{t}:{sid}/")
            if page and page["status"] == 200 and sid in page["html"]:
                break
        subj = f"post {sid} ({why}{' of ' + art['slug'] if art else ''})"
        if not page:
            continue
        if re.search(r"/(signup|login|authwall|checkpoint)", page["final_url"]):
            add("WARN", "post", subj, "not publicly visible (redirects to sign-up); can't verify logged out")
            continue
        if page["status"] != 200:
            add("FAIL", "post", subj, f"public post page {page['status']}")
            continue
        pp = parse_post(page["html"])
        if art:
            lid = art["linkedin_id"] or pulse_id(art["original_url"])
            base = (re.search(r"/pulse/([^/?#\"']+)", art["original_url"] or "") or [None, ""])[1].lower().rstrip("/")
            title_hit = norm(art["title"])[:50] in pp["text"]
            if not (f"-{lid}" in page["html"] or (base and base in page["html"].lower()) or title_hit):
                add("FAIL", "placement", subj, f"the post doesn't link or name the article {lid} it is placed on")
        if sh:
            # Text and date
            first = norm(next((l for l in plain(sh["body"]).splitlines() if len(norm(l)) > 30), ""))[:60]
            if first and first not in pp["text"] and first not in norm(pp["description"]):
                add("WARN", "post", subj, "post text not found on the public page (edited?)")
            # Images
            pub_urls = pp["images"] + ([pp["thumbnail"]] if pp["thumbnail"] else [])
            yt = re.search(r"(?:youtu\.be/|youtube\.com/watch\?v=)([\w-]{11})", scalar(sh["fm"], "shared_url") or "")
            if yt:  # a YouTube link card shows the video's own thumbnail
                pub_urls.append(f"https://i.ytimg.com/vi/{yt.group(1)}/hqdefault.jpg")
            pub_hashes = [dhash(d) for d in (F.media(u) for u in pub_urls) if d]
            for img in sorted(sh["dir"].iterdir()):
                if img.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                    continue
                best = min((dist(dhash(img.read_bytes()), h) for h in pub_hashes), default=64)
                if not pub_hashes:
                    add("WARN", "image", subj, f"{img.name}: the public page shows no images to compare")
                elif best > HASH_MAX_DIST:
                    add("FAIL", "image", subj, f"{img.name} doesn't match the post's images on LinkedIn (distance {best})")
        # Comments shown publicly must be in our thread for this post
        t = threads.get(sid)
        if t and pp["comments"]:
            ours = " ".join(norm(c.get("text", "")) for c in t["comments"])
            missing = [c for c in pp["comments"] if norm(c)[:40] and norm(c)[:40] not in ours]
            if len(missing) == len(pp["comments"]):
                add("FAIL", "thread", subj, f"none of the {len(missing)} comments on the public page are in thread {t['thread_urn']}")
            elif missing:
                add("WARN", "thread", subj, f"{len(missing)} public comment(s) not in the thread (newer than the fetch?)")


def check_threads(posts, shares) -> Dict[str, dict]:
    by_post: Dict[str, dict] = {}
    owner: Dict[str, str] = {}
    names: Dict[str, set] = {}
    page_keys = set()
    for p in posts:
        for v in [p["linkedin_id"], pulse_id(p["original_url"])] + [pulse_id(c) for c in p["claims"]]:
            if v:
                page_keys.add(f"article:{v}")
        for sid in p["intro"] + p["also"]:
            page_keys.add(f"share:{sid}")
    for sh in shares:
        page_keys.add(f"share:{sh['id']}")
    for f in sorted(THREADS.glob("*.json")):
        t = json.loads(f.read_text(encoding="utf-8"))
        urn = t["thread_urn"]
        tid = re.search(r"(\d{15,})", urn).group(1)
        by_post[tid] = t
        subj = f"thread {urn}"
        live = [c for c in t["comments"] if not c.get("deleted")]
        for c in t["comments"]:
            if c["id"].startswith("urn:li:comment:") and tid not in c["id"]:
                add("FAIL", "thread", subj, f"comment {c['id']} belongs to another post")
            if c["id"] in owner and owner[c["id"]] != urn:
                add("FAIL", "thread", subj, f"comment {c['id']} also in {owner[c['id']]}")
            owner[c["id"]] = urn
            a = c.get("author") or {}
            prof = (a.get("profile_url") or "").rstrip("/").lower()
            if prof:
                names.setdefault(prof, set()).add(a.get("name") or "")
                if bool(a.get("is_self")) != prof.endswith(ME):
                    add("FAIL", "thread", subj, f"comment {c['id']}: is_self={a.get('is_self')} but author is {prof}")
            if c.get("parent_id") and c["parent_id"] not in {x["id"] for x in t["comments"]}:
                add("FAIL", "thread", subj, f"reply {c['id']} has no parent in the thread")
            for m in c.get("media") or []:
                if m.get("file") and not pathlib.Path("public", m["file"]).exists():
                    add("FAIL", "thread", subj, f"comment media {m['file']} missing")
        disp = (t.get("displayed") or {}).get("comments")
        if disp is not None and len(live) < disp:
            add("FAIL" if len(live) < 0.8 * disp else "WARN", "thread", subj, f"{len(live)} comments stored, LinkedIn showed {disp}")
        shown = [k for k in t.get("pages", []) if k in page_keys]
        if not shown:
            add("WARN", "thread", subj, f"shown on no page (pages {t.get('pages')})")
    for prof, ns in names.items():
        ns = {n for n in ns if n}
        if len(ns) > 1 and len({norm(n).split(" ")[0] for n in ns}) > 1:
            add("WARN", "thread", prof, f"one profile, several names: {sorted(ns)}")
    return by_post


def check_dist() -> None:
    dist_dir = pathlib.Path("dist")
    if not dist_dir.exists():
        add("WARN", "site", "dist", "no build output; run npm run build first")
        return
    for html in sorted(dist_dir.rglob("index.html")):
        text = html.read_text(encoding="utf-8", errors="ignore")
        page = "/" + str(html.parent.relative_to(dist_dir))
        for src in re.findall(r"<img[^>]*\ssrc=\"(/blog/[^\"]+)\"", text):
            if not (dist_dir / urllib.parse.unquote(src[len("/blog/"):]).split("?")[0]).exists():
                add("FAIL", "site", page, f"image {src} doesn't exist")
        for href in re.findall(r"<a[^>]*\shref=\"(/blog/(?:posts|shares)/[^\"#?]+)", text):
            if not (dist_dir / href[len("/blog/"):].rstrip("/") / "index.html").exists():
                add("FAIL", "site", page, f"link {href} goes nowhere")


def check_linkmap(posts) -> None:
    """Every LinkedIn article URL in content maps to the page with that id."""
    urls = set()
    for p in posts:
        urls.update(re.findall(r"https?://www\.linkedin\.com/pulse/[^\s)\"'<>]+", p["body"]))
    for f in THREADS.glob("*.json"):
        urls.update(re.findall(r"https?://www\.linkedin\.com/pulse/[^\s)\"'<>\\]+", f.read_text(encoding="utf-8")))
    if not urls:
        return
    js = "import { localUrlFor } from './src/lib/linkmap.mjs'; const urls = JSON.parse(process.argv[1]); console.log(JSON.stringify(urls.map((u) => [u, localUrlFor(u)])));"
    try:
        out = subprocess.run(["node", "--input-type=module", "-e", js, json.dumps(sorted(urls))], capture_output=True, text=True, check=True).stdout
    except Exception as exc:
        add("WARN", "links", "linkmap", f"couldn't run linkmap.mjs: {exc}")
        return
    slug_ids: Dict[str, set] = {}
    for p in posts:
        ids = {x for x in [p["linkedin_id"], pulse_id(p["original_url"])] + [pulse_id(c) for c in p["claims"]] if x}
        slug_ids[p["slug"]] = ids
    for url, local in json.loads(out):
        if not local:
            continue
        lid = pulse_id(url + " ")
        slug = local.rstrip("/").rsplit("/", 1)[-1]
        if lid and slug in slug_ids and lid not in slug_ids[slug]:
            add("FAIL", "links", url, f"rewritten to {local}, which is article {sorted(slug_ids[slug])}")


def check_youtube(posts, shares, F: Fetcher) -> None:
    if not YOUTUBE.exists():
        return
    reg = json.loads(YOUTUBE.read_text(encoding="utf-8")).get("videos", {})
    for key, e in reg.items():
        yid = e.get("youtube_id")
        if not yid:
            continue
        data = None if F.offline else F.s.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={yid}&format=json", timeout=30)
        if data is not None and data.status_code != 200:
            add("FAIL", "youtube", key, f"{yid} doesn't exist or isn't public ({data.status_code})")
            continue
        title = data.json().get("title", "") if data is not None else e.get("title", "")
        if e.get("match") == "duration+title":
            lid = key.split(":")[1].split("#")[0] if key.startswith("article:") else None
            page = next((p for p in posts if lid and (p["linkedin_id"] == lid or pulse_id(p["original_url"]) == lid)), None)
            text = (page["title"] + " " + page["body"]) if page else ""
            if not page:
                sid = re.search(r"(\d{15,})", e.get("share_urn") or "")
                sh = next((s for s in shares if sid and s["id"] == sid.group(1)), None)
                text = (sh["title"] + " " + sh["body"]) if sh else ""
            tw = set(norm(title).split()) - {"the", "a", "and", "of", "for", "on", "in", "with"}
            overlap = len(tw & set(norm(text).split())) / max(1, len(tw))
            if overlap < 0.5:
                add("FAIL", "youtube", key, f"{yid} \"{title}\" shares only {overlap:.0%} of its title with the page")
            elif yid not in text:
                add("WARN", "youtube", key, f"{yid} \"{title}\": the page doesn't link it (match rests on duration+title)")
        elif e.get("match") in ("manual", "uploaded") and not e.get("note") and e.get("match") == "manual":
            add("WARN", "youtube", key, f"manual mapping to {yid} has no note saying why")


def check_live() -> None:
    items = pathlib.Path("linkedin_work/live/Live/items")
    if not items.exists():
        return
    for f in sorted(items.glob("*.json")):
        it = json.loads(f.read_text(encoding="utf-8"))
        recs = []
        if it.get("kind") == "article":
            recs = [it.get("cover")] + it.get("images", []) + [x for v in it.get("videos", []) for x in (v.get("poster_file"), v.get("captions_file"))]
            if not it.get("public_check"):
                add("FAIL", "live", f.name, "no public-page cross-check (fetched before the fix); re-fetch with --refetch --only")
        else:
            for m in it.get("media", []):
                recs += [m if m.get("file") else None, m.get("poster_file"), m.get("captions_file"), m.get("image_file"), m.get("download_file")] + (m.get("page_files") or [])
            recs += (it.get("quote") or {}).get("image_files") or []
        for r in recs:
            if r and r.get("file") and not r.get("from"):
                add("FAIL", "live", f.name, f"{r['file']} has no element provenance")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="no network: repo, threads, dist, linkmap, live provenance; cached pages if any")
    ap.add_argument("--refresh", action="store_true", help="ignore cached public pages")
    ap.add_argument("--max-age-hours", type=float, default=168)
    ap.add_argument("--max-fetch", type=int, default=200, help="public page loads per run")
    ap.add_argument("--only", help="one article's 5-character linkedin_id")
    args = ap.parse_args(argv)

    F = Fetcher(args.offline, args.refresh, args.max_age_hours, args.max_fetch)
    posts, shares = load_posts(), load_shares()
    print(f"[AUDIT] {sum(1 for p in posts if not p['native'])} imported articles, {sum(1 for p in posts if p['native'])} native posts, "
          f"{len(shares)} shares, {len(list(THREADS.glob('*.json')))} threads")
    threads = check_threads(posts, shares)
    check_articles(posts, F, args.only)
    check_posts(posts, shares, F, threads, args.only)
    if not args.only:
        check_youtube(posts, shares, F)
        check_linkmap(posts)
        check_dist()
        check_live()

    WORK.mkdir(parents=True, exist_ok=True)
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "public_fetches": F.fetched,
              "fails": sum(f["severity"] == "FAIL" for f in findings), "warns": sum(f["severity"] == "WARN" for f in findings),
              "findings": findings}
    (WORK / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for f in sorted(findings, key=lambda x: (x["severity"] != "FAIL", x["category"], x["subject"])):
        print(f"{f['severity']:4} {f['category']:9} {f['subject']}: {f['message']}")
    print(f"\n[AUDIT] {report['fails']} FAIL, {report['warns']} WARN ({F.fetched} public fetches). Report: {WORK / 'report.json'}")
    return 1 if report["fails"] else 0


if __name__ == "__main__":
    sys.exit(main())
