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

from linkedin_articles import ArticleData, IntroShareMeta

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

    def __init__(self, export_zip: str, workdir: pathlib.Path, blog_dir: pathlib.Path) -> None:
        self.export_zip = export_zip
        self.workdir = workdir
        self.blog_dir = blog_dir

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
        self._write_share_markdown(shares_list, intro_map)
        return intro_map

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

        print(f"[SHARE] Identified {len(intro_map)} intro blurbs")
        return intro_map

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
    ) -> None:
        intro_share_ids = {meta.share_id for meta in intro_map.values() if meta.share_id}
        standalone_shares = [share for share in shares if share.share_id not in intro_share_ids]

        work_shares_dir = self.workdir / "shares"
        if work_shares_dir.exists():
            shutil.rmtree(work_shares_dir)
        work_shares_dir.mkdir(parents=True, exist_ok=True)

        share_root = self.blog_dir / SHARE_CONTENT_DIR / SHARE_SUBDIR
        if share_root.exists():
            print(f"[SHARE] Clearing existing share content in {share_root}")
            shutil.rmtree(share_root)
        share_root.mkdir(parents=True, exist_ok=True)

        for share in standalone_shares:
            fm_lines = self._build_frontmatter(share)
            body = share.commentary or ""
            if share.shared_url:
                body = f"[Shared link]({share.shared_url})\n\n{body}" if body else f"[Shared link]({share.shared_url})"
            md_content = "\n".join(fm_lines) + "\n\n" + body.strip() + "\n"

            work_path = work_shares_dir / f"{share.slug}.md"
            work_path.write_text(md_content, encoding="utf-8")

            share_dir = share_root / share.slug
            share_dir.mkdir(parents=True, exist_ok=True)
            (share_dir / "index.md").write_text(md_content, encoding="utf-8")

            print(f"[SHARE] Wrote standalone share {share.share_id} → {share_dir.relative_to(self.blog_dir)}")

        print(f"[SHARE] Processed {len(standalone_shares)} standalone shares")

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
