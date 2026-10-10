"""Picks the publish time of the next video.

Two windows a day (channel.yaml -> schedule.windows, IST). Each video gets a random minute inside the next free
window. The time is never the same as the previous day's slot in that window (at least
min_gap_from_yesterday_minutes apart), so the channel never posts at a fixed time.
YouTube itself makes the video public at that time (publishAt), so no GitHub minutes are spent waiting.
"""
import datetime as dt
import random

from .config import WINDOWS, MIN_GAP_FROM_YESTERDAY, MIN_LEAD_MINUTES

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def _mins(hhmm):
    h, m = hhmm.strip().split(":")
    return int(h) * 60 + int(m)


def _windows():
    out = []
    for name, span in WINDOWS.items():
        a, b = span.split("-")
        out.append((name, _mins(a), _mins(b)))
    return sorted(out, key=lambda w: w[1])


def next_slot(slots, now=None, rng=random):
    """slots: list of taken {"date", "window", "minute"}. Returns (aware datetime in IST, slot dict)."""
    now = (now or dt.datetime.now(IST)).astimezone(IST)
    taken = {(s["date"], s["window"]): s["minute"] for s in slots}
    earliest = now + dt.timedelta(minutes=MIN_LEAD_MINUTES)
    for day_off in range(0, 60):
        day = (now + dt.timedelta(days=day_off)).date()
        for name, start, end in _windows():
            if (day.isoformat(), name) in taken:
                continue
            day_start = dt.datetime.combine(day, dt.time(0, 0), IST)
            lo = start
            if day_start + dt.timedelta(minutes=start) < earliest:
                lo = int((earliest - day_start).total_seconds() // 60) + 1
            if lo >= end:
                continue
            prev = taken.get(((day - dt.timedelta(days=1)).isoformat(), name))
            choices = [m for m in range(lo, end) if prev is None or abs(m - prev) >= MIN_GAP_FROM_YESTERDAY]
            if not choices:
                continue
            minute = rng.choice(choices)
            when = day_start + dt.timedelta(minutes=minute)
            return when, {"date": day.isoformat(), "window": name, "minute": minute}
    raise RuntimeError("no free publish slot in the next 60 days")


def to_rfc3339_utc(when):
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
