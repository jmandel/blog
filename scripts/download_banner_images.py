#!/usr/bin/env python3
"""
download_banner_images.py

Normalize LinkedIn banner images so markdown posts reference local assets next to
their markdown files.

The script scans markdown content, downloads any remote banner it finds, and
rewrites the frontmatter to point at `./banner.<ext>` in the same directory as
the markdown file. It is idempotent and safe to run multiple times.
"""

from __future__ import annotations

import os
import pathlib
import re
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

CONTENT_DIR = "src/content/blog"
LINKEDIN_SUBDIR = "linkedin"

BANNER_PATTERN = re.compile(
    r'^banner:\s*["\']?([^"\']+)["\']?\s*$',
    re.MULTILINE | re.IGNORECASE,
)
SLUG_PATTERN = re.compile(r'^slug:\s*["\']?([^"\']+)["\']?\s*$', re.MULTILINE)


def extract_frontmatter_banner(content: str) -> Optional[str]:
    match = BANNER_PATTERN.search(content)
    if match:
        return match.group(1).strip()
    return None


def extract_frontmatter_slug(content: str, fallback: str) -> str:
    match = SLUG_PATTERN.search(content)
    if match:
        return match.group(1).strip()
    return fallback


def is_remote_image_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"}


def determine_image_extension(url: str, content_type: Optional[str]) -> str:
    if content_type:
        lowered = content_type.lower()
        if "jpeg" in lowered or "jpg" in lowered:
            return "jpg"
        if "png" in lowered:
            return "png"
        if "gif" in lowered:
            return "gif"
        if "webp" in lowered:
            return "webp"
    path = urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if path.endswith(ext):
            return ext.lstrip(".")
    return "jpg"


def download_banner_image(url: str, local_path: pathlib.Path) -> bool:
    print(f"  Downloading banner: {url[:60]}...")
    try:
        response = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0 (compatible; banner-fetch/1.0)"},
        )
        response.raise_for_status()
    except Exception as exc:
        print(f"    ✗ Download failed: {exc}")
        return False

    local_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_path, "wb") as handle:
        handle.write(response.content)
    print(f"    ✓ Saved to {local_path}")
    return True


def update_markdown_banner(file_path: pathlib.Path, old_url: str, new_url: str) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"    ✗ Failed to read {file_path}: {exc}")
        return False

    pattern = re.compile(
        r'^banner:\s*["\']?' + re.escape(old_url) + r'["\']?\s*$',
        re.MULTILINE | re.IGNORECASE,
    )
    replacement = f"banner: {new_url}"
    updated_content = pattern.sub(replacement, content)
    if updated_content == content:
        return False

    file_path.write_text(updated_content, encoding="utf-8")
    print(f"    ✓ Updated banner metadata")
    return True


def find_existing_banner(directory: pathlib.Path) -> Optional[pathlib.Path]:
    for ext in ("jpg", "jpeg", "png", "gif", "webp"):
        candidate = directory / f"banner.{ext}"
        if candidate.exists():
            return candidate
    return None


def process_blog_posts() -> None:
    content_root = pathlib.Path(CONTENT_DIR)
    if not content_root.exists():
        print(f"Content directory not found: {CONTENT_DIR}")
        return

    processed = downloaded = updated = 0
    for md_path in sorted(content_root.rglob("*.md")):
        file_path = pathlib.Path(md_path)
        try:
            raw = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"\nProcessing {file_path}")
            print(f"  ✗ Unable to read file: {exc}")
            continue

        slug = extract_frontmatter_slug(raw, file_path.stem)
        print(f"\nProcessing {file_path}")

        banner_url = extract_frontmatter_banner(raw)
        if not banner_url:
            print("  Skipping: no banner field")
            continue
        if not is_remote_image_url(banner_url):
            print("  Skipping: banner already local")
            continue

        processed += 1
        md_dir = file_path.parent

        existing = find_existing_banner(md_dir)
        if existing:
            relative_path = f"./{existing.name}"
            if update_markdown_banner(file_path, banner_url, relative_path):
                updated += 1
            continue

        extension = determine_image_extension(banner_url, None)
        local_path = md_dir / f"banner.{extension}"

        if download_banner_image(banner_url, local_path):
            downloaded += 1
            relative_path = f"./{local_path.name}"
            if update_markdown_banner(file_path, banner_url, relative_path):
                updated += 1
        else:
            print("  Keeping remote URL (download failed)")

    print("\n=== Banner Download Summary ===")
    print(f"Processed remote banners: {processed}")
    print(f"Images downloaded:      {downloaded}")
    print(f"Frontmatter updated:    {updated}")


if __name__ == "__main__":
    print("Downloading banner images for blog posts...")
    process_blog_posts()
    print("Done!")
