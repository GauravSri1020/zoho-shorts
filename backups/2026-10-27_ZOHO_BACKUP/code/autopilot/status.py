"""Pipeline status for the Control Room dashboard ("kitni video kahan hai").

After every robot run whose counts changed, the robot opens ONE NEW small GitHub issue whose TITLE is the whole
PIPELINE line (and closes the previous status issue). Gmail only shows the old messages of one thread, so every
status gets its own issue = its own e-mail; the dashboard reads the newest e-mail from Gmail.
The first line is machine-readable (the dashboard parses it), e.g.
PIPELINE ideas=24 clips=1 editing=0 qa_failed=1 scheduled=3 published=8 total=11 today=2 next=2026-10-14T18:00

Stages:
  ideas      - Research: real problems in research/problem_bank.yaml not made into a Short yet
  clips      - Script ready, waiting for YOUR Flow clips (GitHub issue open)
  editing    - With the video editor: all clips uploaded, being built / build error
  qa_failed  - QA rejected it: retake the bad clips
  scheduled  - On YouTube, goes public later (private + publish time)
  published  - Public on YouTube
  total      - scheduled + published (Shorts made so far)
  today      - Shorts going public today (max = schedule.per_day)
"""
import datetime as dt
import json

from . import state as _state
from .config import CH, ROOT

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
VIDEO_EXT = (".mp4", ".mov", ".webm", ".m4v")
KEYS = ("ideas", "clips", "editing", "qa_failed", "scheduled", "published", "total", "today", "next")
LABELS = {"ideas": "Research - ideas ready", "clips": "Waiting for your Flow clips", "editing": "With the video editor",
          "qa_failed": "QA failed - retake needed", "scheduled": "Scheduled on YouTube", "published": "Published",
          "total": "Total Shorts made", "today": "Going public today", "next": "Next publish time (IST)"}


def _ideas(st):
    try:
        import yaml
        path = ROOT / str(CH.get("problem_bank") or "research/problem_bank.yaml")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return 0
    items = data if isinstance(data, list) else (data.get("problems") or [])
    used = {str(p).strip().lower() for p in st.get("problems", [])}
    return sum(1 for it in items if isinstance(it, dict) and str(it.get("problem", "")).strip().lower() not in used)


def counts(now=None):
    now = (now or dt.datetime.now(IST)).astimezone(IST)
    st = _state.load()
    c = {"ideas": _ideas(st), "clips": 0, "editing": 0, "qa_failed": 0, "scheduled": 0, "published": 0}
    jobs = ROOT / "jobs"
    for jf in (sorted(jobs.glob("*/job.json")) if jobs.exists() else []):
        try:
            job = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        s = str(job.get("status", "")).lower()
        if s in ("done", "uploaded", "uploaded_manually", "skip"):
            continue
        if s == "qa_failed":
            c["qa_failed"] += 1
            continue
        cd = jf.parent / "clips"
        have = len([p for p in cd.iterdir() if p.suffix.lower() in VIDEO_EXT]) if cd.exists() else 0
        c["editing" if have >= len(job.get("clips") or []) else "clips"] += 1
    nxt, today, seen = None, 0, set()
    for s in st.get("slots", []):
        vid = s.get("video_id")
        if not vid or vid in seen or not s.get("date"):
            continue
        seen.add(vid)
        when = (dt.datetime.combine(dt.date.fromisoformat(str(s["date"])), dt.time(0, 0), IST)
                + dt.timedelta(minutes=int(s.get("minute", 0))))
        if when > now:
            c["scheduled"] += 1
            nxt = when if nxt is None or when < nxt else nxt
        else:
            c["published"] += 1
        if when.date() == now.date():
            today += 1
    c["total"] = c["scheduled"] + c["published"]
    c["today"] = today
    c["next"] = nxt.strftime("%Y-%m-%dT%H:%M") if nxt else "-"
    return c


def line(c):
    return "PIPELINE " + " ".join(f"{k}={c[k]}" for k in KEYS)


def post():
    """Opens a new status issue (title = PIPELINE line) when the counts changed and closes the old one.
    Never breaks a run."""
    try:
        from .flow import REPO, _gh
        st = _state.load()
        c = counts()
        txt = line(c)
        if st.get("status_line") == txt:
            print(f"[status] unchanged: {txt}")
            return
        old = st.get("status_issue")
        if old:  # close first, so the newest e-mail is always the new issue
            _gh("PATCH", f"/issues/{old}", {"state": "closed", "state_reason": "completed"})
        table = "\n".join(f"| {LABELS[k]} | {c[k]} |" for k in KEYS)
        stamp = dt.datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
        iss = _gh("POST", "/issues", {
            "title": f"📊 {txt}",
            "body": f"{txt}\n\n| Stage | Count |\n|---|---|\n{table}\n\nPosted {stamp}. The Control Room dashboard "
                    "reads the newest of these e-mails. The robot closes the old status issue by itself.",
            "assignees": [REPO.split("/")[0]]})
        if iss.get("number"):
            st["status_issue"], st["status_line"] = iss["number"], txt
            _state.save(st)
        print(f"[status] {txt}")
    except Exception as e:
        print(f"[status] skipped: {str(e)[:200]}")
