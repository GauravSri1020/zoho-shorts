"""Entry point.
  python -m autopilot.main daily [--count 1] [--no-upload]   research -> script -> QA -> Flow prompts -> GitHub issue
                                                              (GitHub e-mails it; you make the clips in Google Flow)
  python -m autopilot.main assemble                           your uploaded Flow clips -> finished Short -> QA ->
                                                              scheduled YouTube upload (starts by itself on upload)
  python -m autopilot.main comments                           reply to new comments
"""
import argparse
import datetime as dt
import json
import shutil
import sys
import traceback

from . import flow, google_apis as g, notify, schedule, state, writer
from .config import (OUT_DIR, CHANNEL_NAME, CHANNEL_HANDLE, HASHTAGS, NICHE, DISCLAIMER, SCRIPTS_PER_DAY,
                     MAX_VIDEO_SECONDS)

IST = schedule.IST
AI_DISCLOSURE = "This video uses an AI-generated presenter and voice."


def _yt_safe(text):
    """YouTube rejects titles/descriptions containing < or > (Zoho menu paths use '>')."""
    return text.replace("<", "‹").replace(">", "›")


def build_title(sc):
    t = (sc.get("title") or f"{CHANNEL_NAME} - Zoho fix").replace("#Shorts", "").strip()
    return _yt_safe((t[:88] + " #Shorts").strip())


def build_description(sc, angle):
    lines = [(sc.get("description") or "").strip(), ""]
    steps = angle.get("steps") or []
    if steps:
        lines += [f"{i + 1}. {s}" for i, s in enumerate(steps)] + [""]
    code = sc.get("code")
    if isinstance(code, dict) and code.get("content") and len(code["content"]) < 2500:
        lines += [f"Code ({code.get('language', '')}) - {code.get('where_to_paste', '')}:", code["content"], ""]
    lines.append(f"Daily Zoho fixes - follow {CHANNEL_HANDLE}")
    if angle.get("story"):
        lines += ["", f"Question that inspired this: {angle['story']['link']}"]
    lines += ["", AI_DISCLOSURE]
    if DISCLAIMER:
        lines.append(DISCLAIMER)
    lines += ["", " ".join("#" + h.lstrip("#").replace(" ", "") for h in HASHTAGS)]
    return _yt_safe("\n".join(lines))


def _lines(sc):
    return [l for l in sc.get("lines", []) if (l.get("say") or l.get("tts"))]


def run_comments(max_replies=15):
    """Replies to new comments automatically (the AI skips anything risky). Telegram only if it breaks."""
    yt = g.youtube()
    st = state.load()
    seen = set(st["seen_comments"])
    me = g.my_channel_id(yt)
    titles = {s.get("video_id"): s.get("title") for s in st["slots"]}
    posted = failed = 0
    for th in g.recent_comment_threads(yt, me):
        if posted >= max_replies:
            break
        top = th["snippet"]["topLevelComment"]
        cid, sn = top["id"], top["snippet"]
        if cid in seen or sn.get("authorChannelId", {}).get("value") == me:
            continue
        seen.add(cid)
        replies = th.get("replies", {}).get("comments", [])
        if any(r["snippet"].get("authorChannelId", {}).get("value") == me for r in replies):
            continue
        try:
            text = writer.suggest_reply(sn.get("textDisplay", ""), titles.get(sn.get("videoId"), CHANNEL_NAME))
            if text:
                g.reply(yt, cid, text)
                posted += 1
        except Exception as e:
            failed += 1
            print(f"[comments] {cid} failed: {e}")
    st["seen_comments"] = list(seen)
    state.save(st)
    print(f"[comments] {posted} replies posted, {failed} failed")
    if failed > 3:
        notify.send(f"⚠️ {CHANNEL_NAME}: {failed} comment replies fail ho gaye. GitHub Actions ka log dekh.")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("task", choices=["daily", "comments", "assemble"])
    p.add_argument("--count", type=int, default=SCRIPTS_PER_DAY)
    p.add_argument("--no-upload", action="store_true")
    a = p.parse_args(argv)
    try:
        if a.task == "daily":          # script + Flow prompts -> GitHub issue (you make the clips in Flow)
            flow.prepare(max(1, a.count), not a.no_upload)
        elif a.task == "assemble":     # your Flow clips -> finished Short -> QA -> YouTube
            flow.finish()
        else:
            run_comments()
    except Exception as e:
        notify.send(f"⚠️ {CHANNEL_NAME} {a.task} FAILED: {type(e).__name__}: {str(e)[:300]}")
        raise


if __name__ == "__main__":
    sys.exit(main())
