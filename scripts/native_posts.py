#!/usr/bin/env python3
"""Native (hand-written) posts that supersede LinkedIn imports.

A native post lives anywhere under src/content/blog/ except linkedin/,
e.g. src/content/blog/my-post/index.md. It claims a LinkedIn article when

- its frontmatter lists the article in `supersedes_linkedin:` (a LinkedIn
  URL, linkedin_id, imported slug or exact title; one value or a list), or
- its slug, or the slug of its title, equals the article's slug.

The importer skips claimed articles, removes any earlier import of them,
and copies their LinkedIn metadata (original_url, linkedin_id, intro_share)
into the native post's frontmatter when those fields are missing.
"""

from __future__ import annotations

import difflib
import pathlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional

from slugify import slugify

CONTENT_DIR = "src/content/blog"
LINKEDIN_SUBDIR = "linkedin"

# Title words too common to signal that two posts are the same story.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from", "how",
    "i", "in", "is", "it", "my", "of", "on", "or", "our", "the", "to", "we",
    "what", "why", "with", "you", "your",
}


@dataclass
class NativePost:
    path: pathlib.Path  # index.md
    title: str
    slug: str
    date: Optional[datetime]
    claims: List[str] = field(default_factory=list)
    has_original_url: bool = False
    has_linkedin_id: bool = False
    has_intro_share: bool = False

    @property
    def keys(self) -> set[str]:
        keys = {self.slug, slugify(self.title, lowercase=True)}
        keys.update(_normalize_claim(c) for c in self.claims)
        return {k for k in keys if k}


def _normalize_claim(value: str) -> str:
    """Reduce a LinkedIn URL, id, slug or title to a comparable key."""
    value = value.strip().strip('"').strip("'")
    m = re.search(r"linkedin\.com/pulse/([^/?#]+)", value)
    if m:
        return "pulse:" + m.group(1).lower()
    if re.fullmatch(r"[a-z0-9]{5}", value):
        return "id:" + value
    return slugify(value, lowercase=True)


def article_keys(article) -> set[str]:
    keys = {article.slug, slugify(article.title, lowercase=True), "pulse:" + article.basename.lower()}
    if article.linkedin_id:
        keys.add("id:" + article.linkedin_id)
    return keys


def _frontmatter(text: str) -> Optional[str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else None


def _scalar(fm: str, key: str) -> Optional[str]:
    m = re.search(rf"^{key}:[ \t]*(.*?)\s*$", fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def _list(fm: str, key: str) -> List[str]:
    m = re.search(rf"^{key}:[ \t]*(.*?)\n((?:[ \t]+-.*\n?)*)", fm + "\n", re.MULTILINE)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline.startswith("["):
        return [v.strip().strip('"').strip("'") for v in inline.strip("[]").split(",") if v.strip()]
    if inline:
        return [inline.strip('"').strip("'")]
    return [line.strip()[1:].strip().strip('"').strip("'") for line in m.group(2).splitlines() if line.strip()]


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw[:19])
    except ValueError:
        try:
            return datetime.fromisoformat(raw[:10])
        except ValueError:
            return None


def load_native_posts(blog_dir: pathlib.Path) -> List[NativePost]:
    root = blog_dir / CONTENT_DIR
    posts: List[NativePost] = []
    for path in sorted(root.rglob("index.md*")):
        if path.relative_to(root).parts[0] == LINKEDIN_SUBDIR:
            continue
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            continue
        title = _scalar(fm, "title") or path.parent.name
        posts.append(
            NativePost(
                path=path,
                title=title,
                slug=_scalar(fm, "slug") or path.parent.name,
                date=_parse_date(_scalar(fm, "date")),
                claims=_list(fm, "supersedes_linkedin"),
                has_original_url=_scalar(fm, "original_url") is not None,
                has_linkedin_id=_scalar(fm, "linkedin_id") is not None,
                has_intro_share=re.search(r"^intro_share:", fm, re.MULTILINE) is not None,
            )
        )
    return posts


def find_claim(article, natives: Iterable[NativePost]) -> Optional[NativePost]:
    keys = article_keys(article)
    for native in natives:
        if native.keys & keys:
            return native
    return None


def fill_linkedin_metadata(native: NativePost, article, intro_lines: List[str]) -> None:
    """Add the LinkedIn link fields the native post doesn't set itself."""
    added: List[str] = []
    if not native.has_original_url:
        added.append(f'original_url: "{article.original_url}"')
    if not native.has_linkedin_id and article.linkedin_id:
        added.append(f"linkedin_id: {article.linkedin_id}")
    if not native.has_intro_share and intro_lines:
        added.extend(intro_lines)
    if not added:
        return
    text = native.path.read_text(encoding="utf-8")
    end = text.index("\n---\n", 4)
    native.path.write_text(text[:end] + "\n" + "\n".join(added) + text[end:], encoding="utf-8")
    native.has_original_url = True
    native.has_linkedin_id = native.has_linkedin_id or bool(article.linkedin_id)
    native.has_intro_share = native.has_intro_share or bool(intro_lines)
    print(f"[NATIVE] Added LinkedIn metadata to {native.path.parent.name}: "
          + ", ".join(line.split(":")[0] for line in added if not line.startswith(" ")))


def _words(title: str) -> set[str]:
    return {w for w in slugify(title, lowercase=True).split("-") if w not in STOPWORDS and len(w) > 2}


def report_possible_overlaps(unclaimed_articles, natives: Iterable[NativePost]) -> None:
    """Print LinkedIn articles that may be the same story as a native post.

    A pair is reported when the dates are within a week, or the titles
    share most of their words, or the dates are within 90 days and the
    titles are somewhat alike (LinkedIn versions often go up later with
    a reworded headline).

    Only native posts not yet linked to LinkedIn are checked. An agent
    should read each pair and, if they are the same story, add the article
    to the native post's `supersedes_linkedin:` and re-run the import.
    """
    candidates = [n for n in natives if not n.has_original_url]
    pairs = []
    for article in unclaimed_articles:
        for native in candidates:
            a, n = _words(article.title), _words(native.title)
            overlap = len(a & n) / max(1, min(len(a), len(n)))
            ratio = difflib.SequenceMatcher(None, article.slug, slugify(native.title, lowercase=True)).ratio()
            days = abs((article.created_at - native.date).days) if native.date else None
            near = days is not None and days <= 90
            if (days is not None and days <= 7) or overlap >= 0.8 or (near and (overlap >= 0.4 or ratio >= 0.5)):
                pairs.append((native, article, overlap, ratio, days))
    if not pairs:
        return
    print("\n[OVERLAP?] LinkedIn articles that may duplicate a native post (check each one):")
    for native, article, overlap, ratio, days in pairs:
        when = f"{days} days apart" if days is not None else "native post has no date"
        print(f"  native {native.path.parent.name!r} ({native.title!r})\n"
              f"    vs linkedin {article.slug!r} ({article.title!r})\n"
              f"    title words {overlap:.0%}, title similarity {ratio:.2f}, {when}\n"
              f"    same story? add to the native post:  supersedes_linkedin: \"{article.original_url}\"")
