#!/usr/bin/env python3
"""Read the Live/ sidecar that scripts/linkedin_live_fetch.ts adds to an export.

A normal LinkedIn export has no Live/manifest.json, so load() returns None
and the importer behaves exactly as before. When present, the sidecar
supplies what the export loses: real cover and inline images, post media,
the true post→article links, Josh's "link in comments", and the comment
threads (merged into src/data/linkedin/ by linkedin_threads.py).
"""

from __future__ import annotations

import json
import re
import zipfile
from typing import Dict, List, Optional

MANIFEST = "Live/manifest.json"


def _id(urn: Optional[str]) -> str:
    m = re.search(r"(\d{10,})", urn or "")
    return m.group(1) if m else ""


class LiveSidecar:
    def __init__(self, zf: zipfile.ZipFile, manifest: dict) -> None:
        self.zf = zf
        self.manifest = manifest
        self.names = set(zf.namelist())
        self.articles: Dict[str, dict] = {a["basename"].lower(): a for a in manifest.get("articles", [])}
        self.posts_by_share: Dict[str, dict] = {}
        for p in manifest.get("posts", []):
            if p.get("share_urn"):
                self.posts_by_share[_id(p["share_urn"])] = p

    @classmethod
    def load(cls, export_zip: str) -> Optional["LiveSidecar"]:
        zf = zipfile.ZipFile(export_zip)
        if MANIFEST not in zf.namelist():
            zf.close()
            return None
        manifest = json.loads(zf.read(MANIFEST).decode("utf-8"))
        print(f"[LIVE] Sidecar found: {len(manifest.get('articles', []))} articles, "
              f"{len(manifest.get('posts', []))} posts, {len(manifest.get('threads', {}))} threads")
        return cls(zf, manifest)

    def media(self, path: Optional[str]) -> Optional[bytes]:
        if path and path in self.names:
            return self.zf.read(path)
        return None

    def article(self, basename: str) -> Optional[dict]:
        return self.articles.get(basename.lower())

    def post(self, share_id: str) -> Optional[dict]:
        return self.posts_by_share.get(share_id)

    def intro_share_ids(self) -> Dict[str, str]:
        """Article basename → share id of the post that announced it.

        Ground truth from the article page: its comments hang off that
        post (same thread URN)."""
        out: Dict[str, str] = {}
        for a in self.manifest.get("articles", []):
            if a.get("thread_urn"):
                out[a["basename"].lower()] = _id(a["thread_urn"])
        return out

    def threads(self) -> List[dict]:
        out = []
        for name in sorted(self.names):
            if name.startswith("Live/threads/") and name.endswith(".json"):
                out.append(json.loads(self.zf.read(name).decode("utf-8")))
        return out

    def relations(self) -> List[dict]:
        return list(self.manifest.get("relations", []))
