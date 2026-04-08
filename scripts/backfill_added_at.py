#!/usr/bin/env python3
"""Backfill `added_at` frontmatter on existing LinkedIn blog posts.

For every src/content/blog/linkedin/*/index.md that does not already have
an `added_at` value, runs `git log --diff-filter=A --format=%aI -- <path>`
to find the commit that first added the file and uses that date. Files
with no git history fall back to today's date.

Idempotent: skips any post that already has `added_at`.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
from datetime import date, datetime

CONTENT_DIR = pathlib.Path("src/content/blog/linkedin")

ADDED_AT_RE = re.compile(r"^added_at:\s*", re.MULTILINE)
LINKEDIN_ID_RE = re.compile(r"^linkedin_id:\s*(.+)$", re.MULTILINE)
ORIGINAL_URL_RE = re.compile(r"^original_url:\s*(.+)$", re.MULTILINE)


def git_first_added(path: pathlib.Path) -> str | None:
    """Return ISO date string of the commit that first added the path, or None."""
    try:
        result = subprocess.run(
            [
                "git", "log",
                "--diff-filter=A",
                "--follow",
                "--format=%aI",
                "--",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None
    # --follow can return multiple entries; the oldest (the true add) is last.
    return lines[-1]


def split_frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end], text[end + 4:]


def insert_added_at(front: str, added_at_iso: str) -> str:
    """Insert `added_at` immediately after `date:` for consistency."""
    lines = front.splitlines()
    out: list[str] = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and line.startswith("date:"):
            out.append(f"added_at: {added_at_iso}")
            inserted = True
    if not inserted:
        # No date line? Just append at the end.
        out.append(f"added_at: {added_at_iso}")
    return "\n".join(out)


def backfill_one(md_path: pathlib.Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    split = split_frontmatter(text)
    if not split:
        return "skip-no-frontmatter"
    front, body = split
    if ADDED_AT_RE.search(front):
        return "already-has"

    iso = git_first_added(md_path)
    source = "git"
    if not iso:
        iso = date.today().isoformat()
        source = "today"
    else:
        # Normalize to YYYY-MM-DD (strip time/tz for readability).
        try:
            iso = datetime.fromisoformat(iso).date().isoformat()
        except ValueError:
            pass

    new_front = insert_added_at(front, iso)
    md_path.write_text("---" + new_front + "\n---" + body, encoding="utf-8")
    return f"added ({source}): {iso}"


def main() -> int:
    if not CONTENT_DIR.exists():
        print(f"Content dir not found: {CONTENT_DIR}")
        return 1

    dirs = sorted(d for d in CONTENT_DIR.iterdir() if d.is_dir())
    touched = 0
    skipped = 0
    for d in dirs:
        md = d / "index.md"
        if not md.exists():
            continue
        result = backfill_one(md)
        if result == "already-has":
            skipped += 1
        else:
            touched += 1
            print(f"[{d.name}] {result}")
    print(f"\n[SUMMARY] touched={touched} already-had={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
