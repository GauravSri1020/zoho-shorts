"""Picks the publish time of the next video.

FIXED publish times every day (channel.yaml -> schedule.times, IST) and never more than schedule.per_day videos
on one day (default 2). A day's count comes from state/state.json AND from what is really scheduled / published on
the YouTube channel (manual uploads, uploads of parallel runs, old slot names) - so a day can never get 3-4 videos.
YouTube itself makes the video public at that time (publishAt), so no GitHub minutes are spent waiting.
"""
import datetime as dt

from .config import CH, MIN_LEAD_MINUTES

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
_S = CH.get("schedule", {}) or {}
TIMES = sorted({str(t).strip() for t in (_S.get("times") or ["18:00", "22:00"])})
PER_DAY = max(1, min(int(_S.get("per_day", len(TIMES))), len(TIMES)))
CLASH_MINUTES = 60  # a fixed time counts as taken if a video already goes public within an hour of it


def _mins(hhmm):
    h, m = hhmm.strip().split(":")
    return int(h) * 60 + int(m)


def taken_by_day(slots, youtube_times=None):
    """{"YYYY-MM-DD": [minute of day, ...]} of every video already going public, IST.
    slots: state["slots"] ({"date", "minute", "video_id"}); youtube_times: [(video_id, aware datetime)] from
    google_apis.scheduled_times() - a video in both lists is counted once."""
    out, seen = {}, set()
    for s in slots or []:
        if s.get("date") is None:
            continue
        out.setdefault(str(s["date"]), []).append(int(s.get("minute", -9999)))
        if s.get("video_id"):
            seen.add(s["video_id"])
    for vid, when in youtube_times or []:
        if vid in seen:
            continue
        t = when.astimezone(IST)
        out.setdefault(t.date().isoformat(), []).append(t.hour * 60 + t.minute)
    return out


def next_slot(slots, now=None, youtube_times=None, rng=None):
    """Next free fixed time. Returns (aware datetime in IST, slot dict {"date", "window", "minute"})."""
    now = (now or dt.datetime.now(IST)).astimezone(IST)
    taken = taken_by_day(slots, youtube_times)
    earliest = now + dt.timedelta(minutes=MIN_LEAD_MINUTES)
    for day_off in range(0, 90):
        day = (now + dt.timedelta(days=day_off)).date()
        used = taken.get(day.isoformat(), [])
        if len(used) >= PER_DAY:
            continue
        day_start = dt.datetime.combine(day, dt.time(0, 0), IST)
        for t in TIMES:
            m = _mins(t)
            if any(abs(m - u) < CLASH_MINUTES for u in used):
                continue
            when = day_start + dt.timedelta(minutes=m)
            if when < earliest:
                continue
            return when, {"date": day.isoformat(), "window": t, "minute": m}
    raise RuntimeError("no free publish slot in the next 90 days")


def to_rfc3339_utc(when):
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
