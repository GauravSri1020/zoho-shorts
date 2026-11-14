"""Buffer keeper (no AI needed): keeps at least BUFFER_DAYS of Shorts + long videos scheduled on YouTube.

  python -m longform.keeper            (run by .github/workflows/keeper.yml every day)

Counts what is already scheduled in the future (docs/longform/shorts-uploaded/*.json, docs/longform/uploaded/*.json),
and when that is less than the buffer it moves the next ready scripts out of the queue:
  docs/longform/queue/shorts/*.json  -> docs/longform/shorts/      (then workflow shorts-daily makes + schedules them)
  docs/longform/queue/long/<id>.json -> docs/longform/daily/       (then workflow longform-daily)
Queue files are full, already fact-checked scripts (long: a daily request {"id","script"}; publish_at is set here).
Writes the files to dispatch into out/keeper.json; when the queue runs low it says so (the workflow opens an issue).
"""
import datetime as dt
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "docs/longform"
SHORTS_PER_DAY, BUFFER_DAYS = 2, 3
LONG_HOUR_UTC = 13          # 18:30 IST


def future(folder):
    now = dt.datetime.now(dt.timezone.utc)
    out = []
    for f in sorted((D / folder).glob("*.json")) if (D / folder).exists() else []:
        try:
            j = json.loads(f.read_text())
            t = dt.datetime.fromisoformat(j["publish_at"].replace("Z", "+00:00"))
        except Exception:
            continue
        if folder == "uploaded" and "#shorts" in str(j.get("title", "")).lower():
            continue                          # old Flow news Shorts were recorded here too
        if t > now:
            out.append(t)
    return sorted(out)


def in_flight(folder, done_folders):
    """Request files pushed but without a result yet (being made right now)."""
    done = {f.stem for d in done_folders if (D / d).exists() for f in (D / d).glob("*.json")}
    return [f for f in sorted((D / folder).glob("*.json")) if f.stem not in done] if (D / folder).exists() else []


def main():
    now = dt.datetime.now(dt.timezone.utc)
    res = {"shorts": [], "long": [], "warn": []}
    # ---- Shorts
    have = len(future("shorts-uploaded")) + len(in_flight("shorts", ["shorts-uploaded", "shorts-failed"]))
    need = SHORTS_PER_DAY * BUFFER_DAYS - have
    q = sorted((D / "queue/shorts").glob("*.json")) if (D / "queue/shorts").exists() else []
    for f in q[:max(0, need)]:
        dst = D / "shorts" / f.name
        subprocess.run(["git", "mv", str(f), str(dst)], check=True)
        res["shorts"].append(str(dst.relative_to(ROOT)))
    # ---- long videos
    fl = future("uploaded")
    busy = in_flight("daily", ["uploaded", "failed", "tested"])
    lq = sorted((D / "queue/long").glob("*.json")) if (D / "queue/long").exists() else []
    if len(fl) + len(busy) < BUFFER_DAYS and lq and not busy:   # one long render at a time
        last = max(fl) if fl else now
        day = max(now + dt.timedelta(hours=3), last + dt.timedelta(hours=20)).date()
        pub = dt.datetime(day.year, day.month, day.day, LONG_HOUR_UTC, 0, tzinfo=dt.timezone.utc)
        if pub < now + dt.timedelta(hours=3):
            pub += dt.timedelta(days=1)
        r = json.loads(lq[0].read_text())
        r["publish_at"] = pub.strftime("%Y-%m-%dT%H:%M:%SZ")
        dst = D / "daily" / lq[0].name
        dst.write_text(json.dumps(r, indent=1))
        subprocess.run(["git", "rm", "-q", str(lq[0])], check=True)
        subprocess.run(["git", "add", str(dst)], check=True)
        res["long"].append(str(dst.relative_to(ROOT)))
    left_s, left_l = len(q) - len(res["shorts"]), len(lq) - len(res["long"])
    if left_s < SHORTS_PER_DAY * 2:
        res["warn"].append(f"only {left_s} Shorts left in docs/longform/queue/shorts")
    if left_l < 2:
        res["warn"].append(f"only {left_l} long videos left in docs/longform/queue/long")
    res.update(scheduled_shorts=have, scheduled_long=len(fl), queue_shorts=left_s, queue_long=left_l)
    Path("out").mkdir(exist_ok=True)
    Path("out/keeper.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
