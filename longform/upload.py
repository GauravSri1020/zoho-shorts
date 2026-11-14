"""Upload a finished long video to YouTube (scheduled, private until publish time) + custom thumbnail.

  python -m longform.upload --video out/final_4k.mp4 --meta previews/<id>.meta.json --thumb previews/<id>-thumb.jpg \
      --publish 2026-11-14T16:30:00Z

meta.json: {"title", "description", "tags": [...]} - written next to the preview by longform.meta after QA.
Uses the Shorts' own YouTube helper (autopilot/google_apis.py, read-only reuse): containsSyntheticMedia = True.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--thumb", default="")
    ap.add_argument("--publish", default="", help="UTC ISO time; empty or in the past -> now + 45 min")
    a = ap.parse_args()
    from autopilot import google_apis as g
    meta = json.loads(Path(a.meta).read_text())
    now = dt.datetime.now(dt.timezone.utc)
    pub = None
    if a.publish:
        pub = dt.datetime.fromisoformat(a.publish.replace("Z", "+00:00"))
    if not pub or pub < now + dt.timedelta(minutes=30):
        pub = now + dt.timedelta(minutes=45)
    publish_at = pub.strftime("%Y-%m-%dT%H:%M:%SZ")
    yt = g.youtube()
    vid = g.upload(yt, a.video, meta["title"], meta["description"], meta.get("tags", []), publish_at)
    print(f"[longform] https://youtube.com/watch?v={vid}  public at {publish_at}")
    if a.thumb and Path(a.thumb).exists():
        g.set_thumbnail(yt, vid, a.thumb)
    out = Path("out")
    out.mkdir(exist_ok=True)
    (out / "uploaded.json").write_text(json.dumps({"video_id": vid, "publish_at": publish_at, "title": meta["title"]}, indent=1))


if __name__ == "__main__":
    main()
