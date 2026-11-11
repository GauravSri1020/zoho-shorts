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
import os
import subprocess
import shutil
import sys
import traceback

from . import flow, google_apis as g, notify, schedule, state, writer
from .config import (OUT_DIR, CHANNEL_NAME, CHANNEL_HANDLE, HASHTAGS, NICHE, DISCLAIMER, SCRIPTS_PER_DAY,
                     MAX_VIDEO_SECONDS, IS_ZOHO, NICHE_ID, NICHES)

IST = schedule.IST
AI_DISCLOSURE = "This video uses an AI-generated presenter and voice."


def _yt_safe(text):
    """YouTube rejects titles/descriptions containing < or > (Zoho menu paths use '>')."""
    return text.replace("<", "‹").replace(">", "›")


def build_title(sc):
    if not IS_ZOHO:  # niche switch - below is the Zoho niche, unchanged
        from .niche_claude_wealth import build_title as nb
        return nb(sc, _yt_safe)
    t = (sc.get("title") or f"{CHANNEL_NAME} - Zoho fix").replace("#Shorts", "").strip()
    return _yt_safe((t[:88] + " #Shorts").strip())


def build_description(sc, angle):
    if not IS_ZOHO:  # niche switch
        from .niche_claude_wealth import build_description as nd
        return nd(sc, angle, _yt_safe, AI_DISCLOSURE)
    lines = [(sc.get("description") or "").strip(), ""]
    steps = angle.get("steps") or []
    if steps:
        lines += [f"{i + 1}. {s}" for i, s in enumerate(steps)] + [""]
    api = sc.get("api")
    if isinstance(api, dict) and (api.get("endpoint") or api.get("name")):
        lines += ["API / tool used:"] + [f"- {k}: {api[k]}" for k in ("name", "endpoint", "scope", "docs")
                                          if api.get(k)] + [""]
    code = sc.get("code")
    if isinstance(code, dict) and code.get("content") and len(code["content"]) < 2500:
        lines += [f"Code ({code.get('language', '')}) - {code.get('where_to_paste', '')}:", code["content"], ""]
    lines.append(f"AI + Zoho automations every day - follow {CHANNEL_HANDLE}")
    story = angle.get("story")
    if story and str(story.get("link", "")).startswith("http"):
        lines += ["", f"What inspired this: {story['link']}"]
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


def _assemble_other_niches():
    """NICHE SWITCH: a Short is always built with the niche it was written for (job.json "niche"; old jobs = zoho).
    flow.finish() above only builds jobs of the active niche; jobs of other niches still waiting are built here, in
    a child run with NICHE=<their niche>, so switching niches never breaks a Short that is half-way."""
    if os.getenv("NICHE_CHILD"):
        return
    others = set()
    for jf in sorted(flow.JOBS.glob("*/job.json")) if flow.JOBS.exists() else []:
        try:
            job = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        n = job.get("niche") or "zoho"
        if n != NICHE_ID and n in NICHES and str(job.get("status", "")).lower() not in flow.SKIP_STATUS:
            others.add(n)
    for n in sorted(others):
        print(f"\n[niche] building waiting '{n}' Shorts with the {n} settings")
        r = subprocess.run([sys.executable, "-m", "autopilot.main", "assemble"],
                           env=dict(os.environ, NICHE=n, NICHE_CHILD="1"))
        if r.returncode:
            print(f"[niche] '{n}' assemble exited with {r.returncode}")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("task", choices=["daily", "comments", "assemble", "ttstest", "fallback"])
    p.add_argument("--hours", type=float, default=20.0, help="fallback: build faceless after this many hours")
    p.add_argument("--count", type=int, default=SCRIPTS_PER_DAY)
    p.add_argument("--no-upload", action="store_true")
    a = p.parse_args(argv)
    if a.task == "ttstest":  # 10 Nov 2026: check the Gemini screen voice without building a Short
        import wave
        from pathlib import Path
        from . import tts
        out = Path(OUT_DIR) / "tts_test.raw.wav"
        out.parent.mkdir(parents=True, exist_ok=True)
        tts._gemini("Zoho Campaigns now supports MCP, so a connected AI agent can build campaigns for you.", out)
        with wave.open(str(out)) as w:
            print(f"[ttstest] OK - Gemini voice {tts.VOICE}: {w.getnframes() / w.getframerate():.1f} s, "
                  f"{w.getframerate()} Hz (models tried in order: {tts.MODELS})")
        return 0
    try:
        if a.task == "fallback":  # 11 Nov 2026: Shorts whose Flow clips did not come -> faceless now
            flow.fallback(a.hours)
            flow.finish()
        elif a.task == "daily":  # script + Flow prompts -> GitHub issue (Claude / Gaurav make the clips in Flow)
            if flow.fallback(20.0):  # yesterday's Shorts still without clips -> faceless first (frees the slots)
                flow.finish()
            flow.prepare(max(1, a.count), not a.no_upload)
            if flow.FACELESS:  # v4: faceless Shorts need no clip -> build, QA and schedule them right away
                flow.finish()
        elif a.task == "assemble":  # your Flow clips -> finished Short -> QA -> YouTube
            flow.finish()
            _assemble_other_niches()
        else:
            run_comments()
    except Exception as e:
        notify.send(f"⚠️ {CHANNEL_NAME} {a.task} FAILED: {type(e).__name__}: {str(e)[:300]}")
        raise
    finally:  # Control room dashboard: how many Shorts are in which stage
        from . import status
        status.post()


if __name__ == "__main__":
    sys.exit(main())
