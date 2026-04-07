#!/usr/bin/env python3
"""Backfill missing article banners by scraping og:image from live LinkedIn URLs.

LinkedIn data exports stopped including article cover photos in Rich_Media.csv
around February 2026, so newer articles import without banners. This script
walks every article markdown file under src/content/blog/linkedin/, finds
those with no banner, fetches the LinkedIn article page, extracts the
og:image meta tag, and saves the image alongside the markdown.

Idempotent: skips any article that already has a banner.* file.
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Optional

import requests

CONTENT_DIR = pathlib.Path("src/content/blog/linkedin")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
OG_IMAGE_RE = re.compile(
    r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def has_banner(article_dir: pathlib.Path) -> bool:
    return any((article_dir / f"banner.{ext}").exists() for ext in ("jpg", "jpeg", "png", "gif", "webp"))


def parse_frontmatter(md_path: pathlib.Path) -> dict[str, str]:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    front = text[3:end]
    out: dict[str, str] = {}
    for line in front.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def extract_og_image(html: str) -> Optional[str]:
    m = OG_IMAGE_RE.search(html)
    if not m:
        return None
    url = m.group(1).replace("&amp;", "&")
    return url


def ext_from_response(resp: requests.Response, fallback: str = ".jpg") -> str:
    ct = resp.headers.get("content-type", "").lower()
    if "svg" in ct:
        return ".svg"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    if "png" in ct:
        return ".png"
    if "gif" in ct:
        return ".gif"
    if "webp" in ct:
        return ".webp"
    return fallback


def is_bogus_banner(content: bytes, content_type: str) -> Optional[str]:
    """Detect LinkedIn placeholder/avatar fallbacks served via og:image.

    Returns a reason string if the image is bogus, otherwise None.
    """
    ct = content_type.lower()
    if "svg" in ct or content[:5] == b"<?xml" or content[:4] == b"<svg":
        return "SVG placeholder"
    # 96x96 PNGs are LinkedIn's profile picture thumbnails (not article covers).
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        try:
            # IHDR chunk starts at byte 8: 4-byte length, 4-byte type "IHDR", then width/height.
            width = int.from_bytes(content[16:20], "big")
            height = int.from_bytes(content[20:24], "big")
            if width <= 200 and height <= 200 and abs(width - height) < 10:
                return f"profile-pic-shaped PNG ({width}x{height})"
        except Exception:
            pass
    if len(content) < 4096:
        return f"too small ({len(content)} bytes)"
    return None


def add_banner_to_frontmatter(md_path: pathlib.Path, banner_filename: str) -> None:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return
    end = text.find("\n---", 3)
    if end == -1:
        return
    front = text[3:end]
    if re.search(r"^banner:\s*", front, re.MULTILINE):
        # Replace existing banner line
        front = re.sub(r"^banner:.*$", f"banner: ./{banner_filename}", front, count=1, flags=re.MULTILINE)
    else:
        front = front.rstrip("\n") + f"\nbanner: ./{banner_filename}\n"
    md_path.write_text("---" + front + "\n---" + text[end + 4:], encoding="utf-8")


def backfill_one(article_dir: pathlib.Path) -> bool:
    md_path = article_dir / "index.md"
    if not md_path.exists():
        return False
    fm = parse_frontmatter(md_path)
    url = fm.get("original_url")
    if not url:
        print(f"[SKIP] {article_dir.name}: no original_url in frontmatter")
        return False

    print(f"[FETCH] {article_dir.name} ← {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[FAIL] {article_dir.name}: fetch error: {exc}")
        return False

    img_url = extract_og_image(resp.text)
    if not img_url:
        print(f"[FAIL] {article_dir.name}: no og:image found")
        return False

    try:
        img_resp = requests.get(img_url, headers=HEADERS, timeout=30)
        img_resp.raise_for_status()
    except Exception as exc:
        print(f"[FAIL] {article_dir.name}: image download error: {exc}")
        return False

    bogus_reason = is_bogus_banner(img_resp.content, img_resp.headers.get("content-type", ""))
    if bogus_reason:
        print(f"[SKIP] {article_dir.name}: og:image is {bogus_reason}, no real cover available")
        return False

    ext = ext_from_response(img_resp)
    banner_filename = f"banner{ext}"
    out_path = article_dir / banner_filename
    out_path.write_bytes(img_resp.content)
    add_banner_to_frontmatter(md_path, banner_filename)
    print(f"[OK]   {article_dir.name}: saved {banner_filename} ({len(img_resp.content)} bytes)")
    return True


def main() -> int:
    if not CONTENT_DIR.exists():
        print(f"Content dir not found: {CONTENT_DIR}")
        return 1

    article_dirs = sorted(d for d in CONTENT_DIR.iterdir() if d.is_dir())
    missing = [d for d in article_dirs if not has_banner(d)]
    print(f"Found {len(missing)} articles missing banners (of {len(article_dirs)} total)\n")

    succeeded = 0
    skipped = 0
    for d in missing:
        if backfill_one(d):
            succeeded += 1
        else:
            skipped += 1

    print(f"\n[SUMMARY] {succeeded} added, {skipped} skipped (no real cover available)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
