#!/usr/bin/env python3
"""Share processing helpers for the LinkedIn import pipeline."""

from __future__ import annotations

import csv
import html
import pathlib
import re
import shutil
import textwrap
import urllib.parse
import zipfile
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Tuple

from slugify import slugify

from linkedin_articles import ArticleData, IntroShareMeta, intro_share_lines

SHARE_CONTENT_DIR = "src/content/shares"
SHARE_SUBDIR = "linkedin"

DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
]

INTRO_MAX_TIME_DIFF_MINUTES = 180  # 3 hours
INTRO_SCORE_THRESHOLD = 0.8


@dataclass
class ShareRecord:
    """Normalized representation of a LinkedIn share/ugc post."""

    share_id: str
    share_url: str
    share_type: str
    posted_at: datetime
    commentary: str
    shared_url: Optional[str]
    media_url: Optional[str]
    visibility: Optional[str]

    @property
    def slug(self) -> str:
        return f"share-{self.share_id}"

    def first_line(self) -> str:
        for line in self.commentary.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return ""


class LinkedInShareProcessor:
    """Process share rows from a LinkedIn export."""

    def __init__(self, export_zip: str, workdir: pathlib.Path, blog_dir: pathlib.Path, live=None) -> None:
        self.export_zip = export_zip
        self.workdir = workdir
        self.blog_dir = blog_dir
        # Optional LiveSidecar: post media, "link in comments", and the true
        # post→article links from a live fetch. None for a normal export.
        self.live = live

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def collect_shares(self) -> List[ShareRecord]:
        records_by_id: Dict[str, ShareRecord] = {}
        with zipfile.ZipFile(self.export_zip) as zf:
            if "Shares.csv" not in zf.namelist():
                print("[SHARE] No Shares.csv found in export; skipping share processing")
                return []
            with zf.open("Shares.csv") as fh:
                reader = csv.DictReader((line.decode("utf-8", "ignore") for line in fh))
                for raw_row in reader:
                    record = self._row_to_share(raw_row)
                    if record:
                        existing = records_by_id.get(record.share_id)
                        if existing is None or len(record.commentary) > len(existing.commentary):
                            records_by_id[record.share_id] = record
        records = sorted(records_by_id.values(), key=lambda s: s.posted_at)
        print(f"[SHARE] Loaded {len(records)} share rows")
        return records

    def process_shares(
        self,
        shares: Iterable[ShareRecord],
        articles: Iterable[ArticleData],
    ) -> Dict[str, IntroShareMeta]:
        shares_list = list(shares)
        articles_list = list(articles)
        intro_map = self._match_intro_shares(shares_list, articles_list)
        skip = self._live_intros_for_known_articles(shares_list, intro_map, articles_list) if self.live else set()
        self._write_share_markdown(shares_list, intro_map, skip)
        return intro_map

    def _live_intros_for_known_articles(
        self,
        shares: List[ShareRecord],
        intro_map: Dict[str, IntroShareMeta],
        articles: List[ArticleData],
    ) -> set:
        """Live zips only: intro posts of articles that aren't in this zip.

        A live fetch skips articles the blog already has, but still lists the
        posts that announced them. Without the article the intro matcher can't
        pair them, and they'd become standalone shares duplicating the
        article's own intro. So: a share that is already some post's
        intro_share is never written standalone; and the earliest live post
        carrying the card of a blog article (imported or native) that has no
        intro_share yet becomes that article's intro_share."""
        in_zip = {a.basename.lower() for a in articles}
        used = {m.share_id for m in intro_map.values() if m.share_id}
        root = self.blog_dir / "src/content/blog"
        entries = []  # (path, pulse basenames, has_intro)
        skip: set = set()
        for path in sorted(root.rglob("index.md")):
            text = path.read_text(encoding="utf-8")
            m = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
            if not m:
                continue
            fm = m.group(1)
            intro_id = re.search(r"^intro_share:\n(?:[ \t]+.*\n)*?[ \t]+share_id:[ \t]*\"?(\d+)", fm + "\n", re.MULTILINE)
            if intro_id:
                skip.add(intro_id.group(1))
            bases = {b.lower().rstrip("/") for b in re.findall(r"linkedin\.com/pulse/([^\"'?#\s]+)", fm)}
            entries.append((path, bases, bool(re.search(r"^intro_share:", fm, re.MULTILINE))))
        claimed: Dict[str, str] = {}
        for share in sorted(shares, key=lambda x: x.posted_at):
            post = self.live.post(share.share_id)
            if not post or share.share_id in used or share.share_id in skip:
                continue
            for media in post.get("media", []):
                if media.get("type") != "article":
                    continue
                base = (re.search(r"/pulse/([^/?#]+)", media.get("url") or "") or [None, ""])[1].lower()
                if not base or base in in_zip or base in claimed:
                    continue
                entry = next((e for e in entries if base in e[1]), None)
                if not entry or entry[2]:
                    continue
                claimed[base] = share.share_id
                lines = intro_share_lines(IntroShareMeta(
                    share_url=share.share_url, share_id=share.share_id, share_type=share.share_type,
                    posted_at=share.posted_at, visibility=share.visibility, shared_url=share.shared_url,
                    commentary=share.commentary or None,
                ))
                text = entry[0].read_text(encoding="utf-8")
                end = text.index("\n---\n", 4)
                entry[0].write_text(text[:end] + "\n" + "\n".join(lines) + text[end:], encoding="utf-8")
                skip.add(share.share_id)
                print(f"[LIVE] Intro post {share.share_id} → {entry[0].parent.relative_to(self.blog_dir)} "
                      f"(earliest post with its article card; the article isn't in this zip)")
        return skip

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _row_to_share(self, row: Dict[str, str]) -> Optional[ShareRecord]:
        share_link = row.get("ShareLink", "").strip()
        if not share_link:
            return None
        decoded_link = urllib.parse.unquote(share_link)
        share_type, share_id = self._extract_share_identity(decoded_link)
        if not share_id:
            return None

        raw_date = (row.get("Date") or "").strip()
        posted_at = self._parse_datetime(raw_date)
        if not posted_at:
            print(f"[SHARE] Skipping row with unparseable date: {raw_date}")
            return None

        commentary = self._clean_commentary(row.get("ShareCommentary", ""))
        shared_url = row.get("SharedUrl", "").strip() or None
        media_url = row.get("MediaUrl", "").strip() or None
        visibility = row.get("Visibility", "").strip() or None

        return ShareRecord(
            share_id=share_id,
            share_url=decoded_link,
            share_type=share_type,
            posted_at=posted_at,
            commentary=commentary,
            shared_url=shared_url,
            media_url=media_url,
            visibility=visibility,
        )

    def _parse_datetime(self, raw: str) -> Optional[datetime]:
        for fmt in DATETIME_FORMATS:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return None

    def _extract_share_identity(self, link: str) -> Tuple[str, str]:
        match = re.search(r"urn:li:([a-zA-Z]+):([0-9]+)", link)
        if not match:
            return ("unknown", link.rsplit('/', 1)[-1])
        return match.group(1), match.group(2)

    def _clean_commentary(self, raw: str) -> str:
        text = (raw or "").replace("\r\n", "\n").replace("\r", "\n")
        lines = []
        for chunk in text.split("\n"):
            stripped = chunk.strip()
            if not stripped:
                lines.append("")
                continue
            # LinkedIn exports frequently wrap each paragraph in quotes.
            quoted = stripped.startswith('"') and stripped.endswith('"') and len(stripped) >= 2
            if quoted:
                stripped = stripped[1:-1]
            stripped = stripped.replace('""', '"')
            if stripped and stripped.endswith('"') and stripped.count('"') % 2 == 1:
                stripped = stripped[:-1]
            lines.append(html.unescape(stripped))
        cleaned = "\n".join(lines).strip()
        return cleaned

    def _match_intro_shares(
        self,
        shares: List[ShareRecord],
        articles: List[ArticleData],
    ) -> Dict[str, IntroShareMeta]:
        intro_map: Dict[str, IntroShareMeta] = {}
        used_share_ids: set[str] = set()
        def article_sort_key(article: ArticleData) -> datetime:
            return article.published_at or article.created_at

        for article in sorted(articles, key=article_sort_key):
            best_candidate: Optional[ShareRecord] = None
            best_score = 0.0
            lower_title = article.title.lower()
            created_time = article.created_at
            published_time = article.published_at or created_time

            for share in shares:
                if share.share_id in used_share_ids:
                    continue
                if share.share_type not in {"ugcPost", "share"}:
                    continue

                time_diff_created = abs((share.posted_at - created_time).total_seconds()) / 60
                time_diff_published = abs((share.posted_at - published_time).total_seconds()) / 60
                time_diff_min = min(time_diff_created, time_diff_published)
                if time_diff_min > INTRO_MAX_TIME_DIFF_MINUTES and not share.shared_url:
                    continue

                score = self._score_share_for_article(
                    share,
                    lower_title,
                    article,
                    created_time,
                    published_time,
                    time_diff_min,
                )
                if score > best_score:
                    best_score = score
                    best_candidate = share

            if best_candidate and best_score >= INTRO_SCORE_THRESHOLD:
                used_share_ids.add(best_candidate.share_id)
                intro_map[article.slug] = IntroShareMeta(
                    share_url=best_candidate.share_url,
                    share_id=best_candidate.share_id,
                    share_type=best_candidate.share_type,
                    posted_at=best_candidate.posted_at,
                    visibility=best_candidate.visibility,
                    shared_url=best_candidate.shared_url,
                    commentary=best_candidate.commentary or None,
                )
                print(
                    f"[SHARE] Matched intro post {best_candidate.share_id} → {article.slug} (score {best_score:.2f})"
                )

        if self.live:
            self._apply_live_intros(intro_map, shares, articles)

        print(f"[SHARE] Identified {len(intro_map)} intro blurbs")
        return intro_map

    def _apply_live_intros(
        self,
        intro_map: Dict[str, IntroShareMeta],
        shares: List[ShareRecord],
        articles: List[ArticleData],
    ) -> None:
        """Replace heuristic intro matches with the live page's ground truth.

        The article page's comments hang off the post that announced it, so
        the live fetch knows exactly which share introduced each article."""
        by_id = {s.share_id: s for s in shares}
        truth = self.live.intro_share_ids()
        for article in articles:
            share_id = truth.get(article.basename.lower())
            if not share_id:
                continue
            current = intro_map.get(article.slug)
            if current and current.share_id == share_id:
                print(f"[LIVE] Intro post for {article.slug} confirmed ({share_id})")
                continue
            share = by_id.get(share_id)
            if not share:
                print(f"[LIVE] Intro post {share_id} for {article.slug} is not in Shares.csv; keeping "
                      f"{current.share_id if current else 'none'}")
                continue
            for slug, meta in list(intro_map.items()):
                if meta.share_id == share_id and slug != article.slug:
                    print(f"[LIVE] Heuristic gave intro post {share_id} to {slug}; it belongs to {article.slug}")
                    del intro_map[slug]
            print(f"[LIVE] Intro post for {article.slug}: live page says {share_id}, heuristic said "
                  f"{current.share_id if current else 'none'}")
            intro_map[article.slug] = IntroShareMeta(
                share_url=share.share_url,
                share_id=share.share_id,
                share_type=share.share_type,
                posted_at=share.posted_at,
                visibility=share.visibility,
                shared_url=share.shared_url,
                commentary=share.commentary or None,
            )

    def _score_share_for_article(
        self,
        share: ShareRecord,
        lower_title: str,
        article: ArticleData,
        created_time: datetime,
        published_time: datetime,
        time_diff_minutes: float,
    ) -> float:
        time_score = max(
            0.0,
            1.0 - min(time_diff_minutes, INTRO_MAX_TIME_DIFF_MINUTES) / INTRO_MAX_TIME_DIFF_MINUTES,
        )

        commentary = share.commentary.lower()
        title_ratio = 0.0
        if lower_title:
            snippet = commentary[: len(lower_title) * 3]
            if snippet:
                title_ratio = SequenceMatcher(None, snippet, lower_title).ratio()
            if lower_title in commentary:
                title_ratio = max(title_ratio, 0.9)
        colon_bonus = 0.2 if not commentary or commentary.strip().endswith(":") else 0.0
        shared_url_bonus = 0.3 if share.shared_url and article.original_url in share.shared_url else 0.0
        return time_score + title_ratio + colon_bonus + shared_url_bonus

    def _write_share_markdown(
        self,
        shares: List[ShareRecord],
        intro_map: Dict[str, IntroShareMeta],
        skip: Optional[set] = None,
    ) -> None:
        intro_share_ids = {meta.share_id for meta in intro_map.values() if meta.share_id} | (skip or set())
        standalone_shares = [share for share in shares if share.share_id not in intro_share_ids]
        # A post of Josh's that carries the card of an article the blog has
        # belongs on that article's page ("Also posted on LinkedIn"), not on a
        # page of its own; otherwise the article shows up twice.
        self.folded: Dict[str, List[ShareRecord]] = {}
        kept = []
        for share in standalone_shares:
            post = self.live.post(share.share_id) if self.live else None
            target = None
            if post and post.get("post_kind", "original") != "repost":
                for m in post.get("media", []):
                    if m.get("type") == "article":
                        target = self._blog_slug_for(m.get("url") or "")
                        if target:
                            break
            if target:
                self.folded.setdefault(target, []).append(share)
                stale = self.blog_dir / SHARE_CONTENT_DIR / SHARE_SUBDIR / share.slug
                if stale.exists():
                    shutil.rmtree(stale)
                print(f"[LIVE] Post {share.share_id} folded into article {target} (it carries the article's card)")
            else:
                kept.append(share)
        standalone_shares = kept
        if skip:
            for share_id in sorted(skip):
                stale = self.blog_dir / SHARE_CONTENT_DIR / SHARE_SUBDIR / f"share-{share_id}"
                if stale.exists() and any(s.share_id == share_id for s in shares):
                    shutil.rmtree(stale)
                    print(f"[LIVE] Removed standalone share-{share_id}: it is an article's intro post")

        work_shares_dir = self.workdir / "shares"
        if work_shares_dir.exists():
            shutil.rmtree(work_shares_dir)
        work_shares_dir.mkdir(parents=True, exist_ok=True)

        share_root = self.blog_dir / SHARE_CONTENT_DIR / SHARE_SUBDIR
        share_root.mkdir(parents=True, exist_ok=True)

        for share in standalone_shares:
            fm_lines = self._build_frontmatter(share)
            body = share.commentary or ""
            if share.shared_url:
                body = f"[Shared link]({share.shared_url})\n\n{body}" if body else f"[Shared link]({share.shared_url})"

            share_dir = share_root / share.slug
            if share_dir.exists():
                shutil.rmtree(share_dir)
            share_dir.mkdir(parents=True, exist_ok=True)

            live_post = self.live.post(share.share_id) if self.live else None
            if live_post:
                extra_fm, extra_body = self._live_post_extras(live_post, share_dir)
                have = {l.split(":", 1)[0] for l in fm_lines if ":" in l and not l.startswith(" ")}
                extra_fm = [l for l in extra_fm if l.split(":", 1)[0] not in have]
                fm_lines = fm_lines[:-1] + extra_fm + fm_lines[-1:]
                if extra_body:
                    body = (body.strip() + "\n\n" + extra_body).strip()
            md_content = "\n".join(fm_lines) + "\n\n" + body.strip() + "\n"

            work_path = work_shares_dir / f"{share.slug}.md"
            work_path.write_text(md_content, encoding="utf-8")
            (share_dir / "index.md").write_text(md_content, encoding="utf-8")

            print(f"[SHARE] Wrote standalone share {share.share_id} → {share_dir.relative_to(self.blog_dir)}")

        print(f"[SHARE] Processed {len(standalone_shares)} standalone shares")

    def _live_post_extras(self, post: dict, share_dir: pathlib.Path) -> Tuple[List[str], str]:
        """Frontmatter lines and markdown for what the export lacks: media
        files, video, documents, polls, the quoted post, "link in comments"."""
        fm: List[str] = []
        parts: List[str] = []
        q = lambda v: str(v).replace('"', '\\"')

        def save(file_ref: Optional[dict], stem: str) -> Optional[str]:
            data = self.live.media((file_ref or {}).get("file"))
            if not data:
                return None
            ext = pathlib.PurePosixPath(file_ref["file"]).suffix or ".jpg"
            name = f"{stem}{ext}"
            (share_dir / name).write_bytes(data)
            return name

        def save_thumb(file_ref: Optional[dict], stem: str) -> Optional[str]:
            """A card thumbnail, resized and re-encoded. Never a byte-for-byte
            copy of the original: Astro collapses identical image files, and an
            article's banner then went missing from the build when its card
            on a post page used the same bytes."""
            data = self.live.media((file_ref or {}).get("file"))
            if not data:
                return None
            from io import BytesIO
            from PIL import Image
            img = Image.open(BytesIO(data)).convert("RGB")
            img.thumbnail((720, 720))
            out = BytesIO()
            img.save(out, "JPEG", quality=85)
            name = f"{stem}.jpg"
            (share_dir / name).write_bytes(out.getvalue())
            return name

        images = [m for m in post.get("media", []) if m.get("type") == "image"]
        for i, m in enumerate(images, 1):
            name = save(m, f"image-{i}")
            if name:
                alt = (m.get("alt") or "").replace("]", "")
                parts.append(f"![{'' if alt in ('View image', 'Image') else alt}](./{name})")
        for m in post.get("media", []):
            kind = m.get("type")
            if kind in ("article", "link_preview"):
                # A card for a linked article or page: thumbnail and title,
                # pointing at this blog's copy when the article is here.
                url = m.get("url") or ""
                target = self._blog_url_for(url) or url
                title = (m.get("title") or url).replace("]", ")").replace("[", "(")
                thumb = save_thumb(m.get("image_file"), f"{'article' if kind == 'article' else 'link'}-card")
                card = f"**[{title}]({target})**" if target else f"**{title}**"
                parts.append(f"[![{title}](./{thumb})]({target})\n\n{card}" if thumb and target else card)
            elif kind == "video":
                poster = save(m.get("poster_file"), "video-poster")
                mins = f" ({m['duration_s'] // 60}:{m['duration_s'] % 60:02d})" if m.get("duration_s") else ""
                link = f"[Watch the video on LinkedIn{mins}]({post['url']})"
                parts.append(f"[![Video]({'./' + poster})]({post['url']})\n\n{link}" if poster else link)
                fm.append(f'video_url: "{post["url"]}"')
            elif kind == "document":
                pages = [save(p, f"document-page-{i}") for i, p in enumerate(m.get("page_files") or [], 1)]
                doc = save(m.get("download_file"), "document")
                parts.append(f"**Document:** {m.get('title') or 'attachment'}"
                             + (f" ([download](./{doc}))" if doc else f" ([view on LinkedIn]({post['url']}))"))
                parts.extend(f"![Page {i}](./{p})" for i, p in enumerate(pages, 1) if p)
            elif kind == "poll":
                opts = "\n".join(f"- {o}" for o in m.get("options") or [])
                parts.append(f"**Poll:** {m.get('question') or ''}\n\n{opts}".strip())
        if post.get("quote"):
            quote = post["quote"]
            who = quote.get("author", {}).get("name") or "another post"
            url = f"https://www.linkedin.com/feed/update/{quote['activity_urn']}/" if quote.get("activity_urn") else None
            if url:
                fm.append(f'quote_of: "{url}"')
            text = (quote.get("text") or "").strip()
            if text:
                quoted = "\n".join("> " + line if line else ">" for line in text.splitlines())
                parts.append(f"> **{who}**{f' ([original on LinkedIn]({url}))' if url else ''}:\n>\n{quoted}")
        link = post.get("first_comment_link")
        if link and link.get("url"):
            fm.append(f'first_comment_link: "{q(link["url"])}"')
            parts.append(f"Link (from my first comment): <{link['url']}>")
        if post.get("edited"):
            fm.append("linkedin_edited: true")
        thumb = next((f for pat in ("image-1.*", "video-poster.*", "article-card.*", "link-card.*")
                      for f in sorted(p.name for p in share_dir.glob(pat))), None)
        if thumb:
            fm.append(f"thumbnail: ./{thumb}")
        return fm, "\n\n".join(parts)

    def _blog_url_for(self, url: str) -> Optional[str]:
        """/blog/posts/<slug> for a LinkedIn article URL that this blog has
        (an imported copy, or a native post that supersedes it)."""
        base = (re.search(r"/pulse/([^/?#]+)", url or "") or [None, None])[1]
        if not base:
            return None
        if not hasattr(self, "_pulse_to_slug"):
            self._pulse_to_slug = {}
            for path in sorted((self.blog_dir / "src/content/blog").rglob("index.md")):
                m = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.DOTALL)
                if not m:
                    continue
                slug = (re.search(r"^slug:[ \t]*(.+)$", m.group(1), re.MULTILINE) or [None, path.parent.name])[1].strip().strip('"')
                for b in re.findall(r"linkedin\.com/pulse/([^\"'?#\s/]+)", m.group(1)):
                    self._pulse_to_slug.setdefault(b.lower(), slug)
        slug = self._pulse_to_slug.get(base.lower().rstrip("/"))
        return f"/blog/posts/{slug}" if slug else None

    def _blog_slug_for(self, url: str) -> Optional[str]:
        local = self._blog_url_for(url)
        return local.rsplit("/", 1)[-1] if local else None

    def backfill_thumbnails(self) -> None:
        """Give earlier share pages that have an image a thumbnail field."""
        root = self.blog_dir / SHARE_CONTENT_DIR / SHARE_SUBDIR
        for md in sorted(root.glob("*/index.md")):
            text = md.read_text(encoding="utf-8")
            end = text.index("\n---\n", 4)
            if re.search(r"^thumbnail:", text[:end], re.MULTILINE):
                continue
            thumb = next((f for pat in ("image-1.*", "video-poster.*", "article-card.*", "link-card.*")
                          for f in sorted(x.name for x in md.parent.glob(pat))), None)
            if thumb:
                md.write_text(text[:end] + f"\nthumbnail: ./{thumb}" + text[end:], encoding="utf-8")

    def write_also_posted(self) -> None:
        """Record folded posts in their article's frontmatter (also_posted).
        Run after articles are written, since imported articles are
        regenerated from scratch."""
        if not getattr(self, "folded", None):
            return
        root = self.blog_dir / "src/content/blog"
        by_slug = {}
        for path in root.rglob("index.md"):
            m = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.DOTALL)
            if m:
                slug = (re.search(r"^slug:[ \t]*(.+)$", m.group(1), re.MULTILINE) or [None, path.parent.name])[1].strip().strip('"')
                by_slug[slug] = path
        q = lambda v: str(v).replace('"', '\\"')
        for slug, shares in self.folded.items():
            path = by_slug.get(slug)
            if not path:
                continue
            text = path.read_text(encoding="utf-8")
            end = text.index("\n---\n", 4)
            fm, rest = text[:end], text[end:]
            # Replace any earlier also_posted block.
            fm = re.sub(r"\nalso_posted:\n(?:[ \t]+.*\n?|-.*\n?)*", "\n", fm + "\n").rstrip("\n")
            lines = ["also_posted:"]
            for share in sorted(shares, key=lambda x: x.posted_at):
                lines += [f'  - share_url: "{share.share_url}"', f'    share_id: "{share.share_id}"',
                          f'    posted_at: "{share.posted_at.isoformat()}"']
                if share.commentary:
                    lines.append("    commentary: |")
                    lines += [f"      {l}" for l in share.commentary.splitlines() or [""]]
            path.write_text(fm + "\n" + "\n".join(lines) + rest, encoding="utf-8")
            print(f"[LIVE] {path.parent.relative_to(self.blog_dir)}: also_posted {len(shares)} post(s)")

    def _build_frontmatter(self, share: ShareRecord) -> List[str]:
        title = self._derive_title(share)
        safe_title = title.replace('"', '\\"')
        fm_lines = [
            "---",
            f'title: "{safe_title}"',
            f"date: {share.posted_at.isoformat()}",
            f"slug: {share.slug}",
            f'share_url: "{share.share_url}"',
            f'share_type: "{share.share_type}"',
        ]
        fm_lines.append(f'share_id: "{share.share_id}"')
        if share.visibility:
            fm_lines.append(f'visibility: "{share.visibility}"')
        if share.shared_url:
            fm_lines.append(f'shared_url: "{share.shared_url}"')
        if share.media_url:
            fm_lines.append(f'media_url: "{share.media_url}"')
        fm_lines.append("---")
        return fm_lines

    def _derive_title(self, share: ShareRecord) -> str:
        first_line = share.first_line()
        if first_line:
            shortened = textwrap.shorten(first_line, width=80, placeholder="…")
            return shortened
        if share.shared_url:
            return share.shared_url
        return f"LinkedIn post on {share.posted_at.strftime('%B %d, %Y')}"
