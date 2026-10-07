#!/usr/bin/env python3
"""Merge LinkedIn comment threads from a live-fetch sidecar into the blog.

Tracked store (published with the site):
  src/data/linkedin/threads/<thread>.json   one file per thread URN
  src/data/linkedin/relations.json          post/article/thread relations
  public/linkedin-media/<sha>.<ext>         images in comments (by hash)

A thread is keyed by the URN of the post its comments hang off
(urn:li:ugcPost:… or urn:li:share:…). An article page shows the comments
of the post that announced it, so the article and that post share one
thread; it is stored once and listed under both pages.

Merging is incremental: comments are matched by id; each records
first_seen / last_seen; a comment missing from a *complete* capture is
kept and marked deleted (not dropped); a partial capture never marks
anything deleted.
"""

from __future__ import annotations

import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Dict, List

DATA_DIR = "src/data/linkedin"
MEDIA_DIR = "public/linkedin-media"

KEEP_FIELDS = ("id", "parent_id", "created_at", "author", "text", "html", "links", "mentions",
               "hashtags", "reactions", "edited")


def _key(urn: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", urn.replace("urn:li:", ""))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def merge_threads(live, blog_dir: pathlib.Path) -> None:
    threads_dir = blog_dir / DATA_DIR / "threads"
    media_dir = blog_dir / MEDIA_DIR
    threads_dir.mkdir(parents=True, exist_ok=True)
    seen_at = live.manifest.get("generated_at") or _now()

    for snap in live.threads():
        urn = snap.get("thread_urn")
        if not urn:
            continue
        path = threads_dir / f"{_key(urn)}.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        old_comments: Dict[str, dict] = {c["id"]: c for c in (old or {}).get("comments", [])}

        merged: Dict[str, dict] = {}
        for c in snap.get("comments", []):
            entry = {k: c.get(k) for k in KEEP_FIELDS}
            entry["media"] = []
            for m in c.get("media", []):
                item = {k: m.get(k) for k in ("type", "alt", "url", "title") if m.get(k)}
                data = live.media(m.get("file"))
                if data:
                    name = pathlib.PurePosixPath(m["file"]).name
                    media_dir.mkdir(parents=True, exist_ok=True)
                    (media_dir / name).write_bytes(data)
                    item["file"] = f"linkedin-media/{name}"
                entry["media"].append(item)
            prev = old_comments.get(c["id"])
            entry["first_seen"] = (prev or {}).get("first_seen") or seen_at
            entry["last_seen"] = seen_at
            merged[c["id"]] = entry

        complete = bool(snap.get("complete"))
        deleted = 0
        for cid, prev in old_comments.items():
            if cid in merged:
                continue
            prev = dict(prev)
            if complete and not prev.get("deleted"):
                prev["deleted"] = True
                prev["deleted_seen"] = seen_at
                deleted += 1
            merged[cid] = prev

        comments = sorted(merged.values(), key=lambda c: (c.get("created_at") or "", c["id"]))
        pages = sorted(set((old or {}).get("pages", [])) | set(snap.get("pages", [])))
        out = {
            "schema": "linkedin-thread/1",
            "thread_urn": urn,
            "url": snap.get("url"),
            "pages": pages,
            "label": snap.get("label") or (old or {}).get("label"),
            "subjects": snap.get("subjects", []),
            "displayed": snap.get("displayed"),
            "captured": snap.get("captured"),
            "complete": complete,
            "sort": snap.get("sort"),
            "first_fetched": (old or {}).get("first_fetched") or seen_at,
            "last_fetched": seen_at,
            "comments": comments,
        }
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        new = sum(1 for c in comments if c.get("first_seen") == seen_at and c["id"] not in old_comments)
        print(f"[THREAD] {urn}: {len(snap.get('comments', []))} captured "
              f"({new} new, {deleted} newly deleted; LinkedIn shows {(snap.get('displayed') or {}).get('comments')})"
              f" → {path.relative_to(blog_dir)}")

    merge_relations(live.relations(), blog_dir / DATA_DIR / "relations.json")


def merge_relations(rels: List[dict], path: pathlib.Path) -> None:
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    key = lambda r: (r.get("from"), r.get("rel"), r.get("to"))
    by_key = {key(r): r for r in old}
    for r in rels:
        by_key[key(r)] = r
    out = sorted(by_key.values(), key=lambda r: tuple(str(x) for x in key(r)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
