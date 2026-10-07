#!/usr/bin/env python3
"""Match LinkedIn videos to copies on Josh's YouTube channel.

The registry, src/data/youtube.json (tracked), says which YouTube video
plays in place of each LinkedIn video on the blog. Keys: the LinkedIn post's
activity URN (urn:li:activity:…), or article:<linkedin_id>#<n> for the n-th
video inside an article. Each entry records the decision and when it was
made, so a video is checked once:

  youtube_id   the equivalent YouTube video, or null ("checked, none")
  match        duration+title | manual | uploaded | none
  checked_at   date of the decision
  candidates   what was considered when nothing matched
  related      non-equivalent videos worth linking ("Longer version on YouTube")

A match needs the duration within ±2 s AND the title sharing words with the
post (and, when known, an upload date near the post's). Duration alone is
not a match: the channel's only 444 s video is an unrelated SMART Health
Check-In demo, the same length as the gpt-live-1 voice demo.

  python3 scripts/youtube_match.py                  # check videos with no entry
  python3 scripts/youtube_match.py --recheck        # check all again
  python3 scripts/youtube_match.py --set urn:li:activity:… <youtube-id> [--uploaded]
  python3 scripts/youtube_match.py --related urn:li:activity:… <youtube-id> "Longer version on YouTube"
  python3 scripts/youtube_match.py --clear urn:li:activity:…
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time
from datetime import date, datetime, timezone

CHANNEL = "UCqV1UeP3YSFQeK3Nu_FGl2w"
REGISTRY = pathlib.Path("src/data/youtube.json")
CACHE = pathlib.Path("linkedin_work/youtube_channel.json")
CACHE_MAX_AGE_S = 24 * 3600
DURATION_TOLERANCE_S = 2
MIN_TITLE_OVERLAP = 0.5  # share of the YouTube title's words found in the post
MAX_UPLOAD_GAP_DAYS = 60

STOP = set("a an and are as at be by for from how i in is it its my of on or our the this to we what why with you your "
           "demo video new part".split())


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9][a-z0-9\-\.]*[a-z0-9]|[a-z0-9]", (text or "").lower()) if w not in STOP and len(w) > 1}


def load_registry() -> dict:
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"schema": "youtube-registry/1", "channel": f"https://www.youtube.com/channel/{CHANNEL}", "videos": {}}


def save_registry(reg: dict) -> None:
    reg["videos"] = dict(sorted(reg["videos"].items()))
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def channel_videos(refresh: bool = False) -> list[dict]:
    if CACHE.exists() and not refresh and time.time() - CACHE.stat().st_mtime < CACHE_MAX_AGE_S:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    print(f"[YT] Listing channel {CHANNEL} with yt-dlp …")
    out = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--print", "%(id)s|%(duration)s|%(title)s",
         f"https://www.youtube.com/channel/{CHANNEL}/videos"],
        capture_output=True, text=True, check=True,
    ).stdout
    vids = []
    for line in out.splitlines():
        vid, dur, title = (line.split("|", 2) + ["", ""])[:3]
        vids.append({"id": vid, "duration": float(dur) if dur not in ("", "NA", "None") else None, "title": title})
    old = {v["id"]: v for v in json.loads(CACHE.read_text(encoding="utf-8"))} if CACHE.exists() else {}
    for v in vids:  # keep upload dates fetched earlier
        if old.get(v["id"], {}).get("upload_date"):
            v["upload_date"] = old[v["id"]]["upload_date"]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(vids, indent=1) + "\n", encoding="utf-8")
    print(f"[YT] {len(vids)} videos cached in {CACHE}")
    return vids


def upload_date(v: dict, vids: list[dict]) -> str | None:
    """Per-video lookup (one request), only for duration candidates; cached."""
    if v.get("upload_date"):
        return v["upload_date"]
    out = subprocess.run(["yt-dlp", "--skip-download", "--print", "%(upload_date)s", f"https://www.youtube.com/watch?v={v['id']}"],
                         capture_output=True, text=True)
    d = out.stdout.strip()
    if re.fullmatch(r"\d{8}", d):
        v["upload_date"] = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        CACHE.write_text(json.dumps(vids, indent=1) + "\n", encoding="utf-8")
    return v.get("upload_date")


def linkedin_videos(live_dir: pathlib.Path) -> dict[str, dict]:
    """LinkedIn videos known to the live fetch, keyed like the registry."""
    out: dict[str, dict] = {}
    items = live_dir / "Live" / "items"
    for f in sorted(items.glob("*.json")) if items.exists() else []:
        it = json.loads(f.read_text(encoding="utf-8"))
        if it.get("kind") == "post" and it.get("activity_urn") and it.get("post_kind") != "repost":
            for m in it.get("media", []):
                if m.get("type") == "video":
                    out[it["activity_urn"]] = {
                        "share_urn": it.get("share_urn"), "url": it.get("url"), "duration_s": m.get("duration_s"),
                        "posted_at": it.get("posted_at"), "text": it.get("text") or "",
                    }
        elif it.get("kind") == "article":
            for v in it.get("videos", []):
                out[f"article:{it['linkedin_id']}#{v['index']}"] = {
                    "url": it.get("url"), "duration_s": v.get("duration_s"), "posted_at": it.get("published_at"),
                    "text": f"{it.get('title', '')} {v.get('caption') or ''} {it.get('subtitle') or ''}",
                }
    return out


def check(key: str, li: dict, vids: list[dict]) -> dict:
    today = date.today().isoformat()
    entry = {"share_urn": li.get("share_urn"), "linkedin_url": li.get("url"), "duration_s": li.get("duration_s"),
             "posted_at": li.get("posted_at"), "checked_at": today}
    dur = li.get("duration_s")
    post_words = words(li.get("text", ""))
    cands = []
    for v in vids:
        if dur is None or v["duration"] is None or abs(v["duration"] - dur) > DURATION_TOLERANCE_S:
            continue
        tw = words(v["title"])
        overlap = len(tw & post_words) / max(1, len(tw))
        c = {"youtube_id": v["id"], "title": v["title"], "duration_s": v["duration"], "title_overlap": round(overlap, 2)}
        reasons = []
        if overlap < MIN_TITLE_OVERLAP:
            reasons.append(f"title shares {overlap:.0%} of its words with the post")
        else:
            up = upload_date(v, vids)
            c["upload_date"] = up
            if up and li.get("posted_at"):
                gap = abs((datetime.fromisoformat(up) - datetime.fromisoformat(li["posted_at"][:10])).days)
                if gap > MAX_UPLOAD_GAP_DAYS:
                    reasons.append(f"uploaded {gap} days from the post")
        c["rejected"] = "; ".join(reasons) or None
        cands.append(c)
    good = [c for c in cands if not c["rejected"]]
    if len(good) == 1:
        entry.update(youtube_id=good[0]["youtube_id"], match="duration+title", title=good[0]["title"],
                     youtube_duration_s=good[0]["duration_s"], youtube_upload_date=good[0].get("upload_date"))
    else:
        entry.update(youtube_id=None, match="none", candidates=cands)
        if len(good) > 1:
            entry["note"] = "several candidates pass; decide with --set"
    return entry


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", default="linkedin_work/live", help="live fetch output dir (Live/items)")
    ap.add_argument("--recheck", action="store_true", help="check videos that already have an entry")
    ap.add_argument("--refresh", action="store_true", help="re-list the channel (cache is kept a day)")
    ap.add_argument("--set", nargs=2, metavar=("KEY", "YOUTUBE_ID"), help="record a manual match")
    ap.add_argument("--uploaded", action="store_true", help="with --set: Josh uploaded this copy (method 'uploaded')")
    ap.add_argument("--note", help="with --set: why (e.g. a different cut the user prefers)")
    ap.add_argument("--related", nargs="+", metavar="ARG", help="KEY YOUTUBE_ID [LABEL]: add a related, non-equivalent video")
    ap.add_argument("--clear", metavar="KEY", help="remove an entry, so it's checked again")
    args = ap.parse_args(argv)

    reg = load_registry()
    videos = reg["videos"]
    known = linkedin_videos(pathlib.Path(args.live))
    today = date.today().isoformat()

    def base(key: str) -> dict:
        if key in videos:
            return dict(videos[key])
        li = known.get(key, {})
        return {"share_urn": li.get("share_urn"), "linkedin_url": li.get("url"), "duration_s": li.get("duration_s"),
                "posted_at": li.get("posted_at"), "youtube_id": None, "match": "none", "checked_at": today}

    if args.set:
        key, yid = args.set
        e = base(key)
        e.pop("candidates", None)
        e.pop("note", None)
        e.update(youtube_id=yid, match="uploaded" if args.uploaded else "manual", checked_at=today)
        if args.note:
            e["note"] = args.note
        # A video that now plays in its place is no longer just "related".
        e["related"] = [r for r in e.get("related", []) if r["youtube_id"] != yid]
        if not e["related"]:
            e.pop("related")
        videos[key] = e
        save_registry(reg)
        print(f"[YT] {key} → https://youtu.be/{yid} ({e["match"]})")
        return 0
    if args.related:
        if len(args.related) < 2:
            ap.error("--related KEY YOUTUBE_ID [LABEL]")
        key, yid = args.related[:2]
        label = args.related[2] if len(args.related) > 2 else "Related video on YouTube"
        e = base(key)
        e["related"] = [r for r in e.get("related", []) if r["youtube_id"] != yid] + [{"youtube_id": yid, "label": label}]
        videos[key] = e
        save_registry(reg)
        print(f"[YT] {key}: related {yid} ({label})")
        return 0
    if args.clear:
        videos.pop(args.clear, None)
        save_registry(reg)
        print(f"[YT] Cleared {args.clear}")
        return 0

    todo = {k: v for k, v in known.items() if args.recheck or k not in videos}
    if not todo:
        print(f"[YT] All {len(known)} LinkedIn videos already have registry entries (--recheck to redo).")
        return 0
    vids = channel_videos(args.refresh)
    for key, li in sorted(todo.items()):
        old = videos.get(key, {})
        if old.get("match") in ("manual", "uploaded") and not args.recheck:
            continue
        entry = check(key, li, vids)
        if old.get("related"):
            entry["related"] = old["related"]
        videos[key] = entry
        dur = li.get("duration_s")
        if entry["youtube_id"]:
            print(f"[YT] MATCH {key} ({dur}s) → {entry['youtube_id']} \"{entry['title']}\" (duration+title)")
        else:
            print(f"[YT] NONE  {key} ({dur}s, posted {str(li.get('posted_at'))[:10]}): \"{li['text'][:70]}…\"")
            for c in entry["candidates"]:
                print(f"        candidate {c['youtube_id']} {c['duration_s']:.0f}s \"{c['title']}\": "
                      f"{c['rejected'] or 'passes (ambiguous)'}")
            if not entry["candidates"]:
                print(f"        no channel video within ±{DURATION_TOLERANCE_S}s")
            print(f"        after uploading a copy: python3 scripts/youtube_match.py --set {key} <youtube-id> --uploaded")
    save_registry(reg)
    print(f"[YT] Registry: {REGISTRY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
