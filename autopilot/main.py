"""Entry point. Fully automatic: nobody records, reads or reviews anything.
  python -m autopilot.main daily [--count 2] [--no-upload]   research -> script -> QA -> voice -> avatar ->
                                                              video -> QA -> scheduled upload (AI label on)
  python -m autopilot.main comments                           reply to new comments
  python -m autopilot.main photos                             photo agent: new scenes of you (weekly)
Telegram / email only when something goes wrong.
"""
import argparse
import datetime as dt
import json
import shutil
import sys
import traceback

from . import avatar, editor, google_apis as g, notify, photos, research, schedule, state, voice, writer
from .config import (OUT_DIR, CHANNEL_NAME, CHANNEL_HANDLE, HASHTAGS, NICHE, DISCLAIMER, SCRIPTS_PER_DAY,
                     MAX_VIDEO_SECONDS)

IST = schedule.IST
AI_DISCLOSURE = (f"Is video mein {CHANNEL_NAME} ka AI avatar aur AI voice hai. "
                 "This video uses an AI-generated presenter and voice.")


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


def make_video(sc, work, st):
    """script -> voice -> captions timing -> avatar -> finished Short, checked by the QA agent."""
    lines = _lines(sc)
    wav, _ = voice.synthesize(lines, work / "voice", MAX_VIDEO_SECONDS)
    words = editor.romanize_if_needed(editor.transcribe(wav, work))
    dur = voice.duration(wav)
    mp4 = work / "short.mp4"
    issues = []
    for force_photo in (False, True):          # lip-sync avatar first, photo-motion backup second
        av, engine, photo = avatar.make(wav, dur, work / "avatar", force_photo=force_photo,
                                        last_photo=st.get("last_photo"))
        editor.render_fullscreen(av, wav, words, work / "edit", mp4)
        problems = editor.check_media(mp4)
        if problems:
            issues = problems
        else:
            verdict = writer.qa_video(mp4, sc)
            print(f"[qa] video ({engine}) approved={verdict['approved']} issues={verdict['issues']}")
            if verdict["approved"]:
                st["last_photo"] = photo
                return mp4, engine
            issues = verdict["issues"]
        if engine == "photo":
            break
    raise RuntimeError("video failed QA: " + "; ".join(map(str, issues))[:300])


def run_daily(count, do_upload):
    st = state.load()
    candidates = research.fetch(st["covered_links"])
    angles = writer.scout(candidates, count + 2, st["problems"])     # spares in case some fail
    print(f"[daily] scout found {len(angles)} angles")
    made, errors = 0, []
    yt = g.youtube() if do_upload else None
    for k, angle in enumerate(angles):
        if made >= count:
            break
        work = OUT_DIR / f"{dt.datetime.now(IST):%Y%m%d-%H%M}-{k + 1}"
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        print(f"\n[daily] === {angle.get('problem')}")
        try:
            sc = writer.approved_script(angle)
            mp4, engine = make_video(sc, work, st)
            title, desc = build_title(sc), build_description(sc, angle)
            (work / "short.json").write_text(json.dumps(
                {"angle": {k2: v for k2, v in angle.items() if k2 != "story"}, "source": angle.get("story"),
                 "script": sc, "title": title, "description": desc, "avatar_engine": engine},
                ensure_ascii=False, indent=1), encoding="utf-8")
            entry = {"problem": angle["problem"], "title": title, "engine": engine,
                     "created": dt.datetime.now(IST).isoformat()}
            if do_upload:
                when, slot = schedule.next_slot(st["slots"])
                tags = list(sc.get("tags") or []) + ["Zoho", "Shorts"]
                vid = g.upload(yt, mp4, title, desc, tags, schedule.to_rfc3339_utc(when))
                st["slots"].append(slot | {"video_id": vid, "title": title})
                entry |= {"video_id": vid, "publish_at": when.isoformat()}
                print(f"[daily] scheduled for {when:%d %b %I:%M %p} IST: https://youtube.com/shorts/{vid}")
            st["scripts"][f"S{st['next_id']:04d}"] = entry
            st["next_id"] += 1
            st["problems"].append(angle["problem"])
            if angle.get("story"):
                st["covered_links"].append(angle["story"]["link"])
            made += 1
        except Exception as e:
            traceback.print_exc()
            errors.append(f"{angle.get('problem', '')[:60]}: {type(e).__name__}: {str(e)[:200]}")
        finally:
            shutil.rmtree(work / "edit", ignore_errors=True)
            shutil.rmtree(work / "avatar" / "sadtalker", ignore_errors=True)
        state.save(st)

    print(f"[daily] done: {made}/{count} Shorts")
    if made < count:
        notify.send(f"⚠️ {CHANNEL_NAME}: aaj {count} mein se sirf {made} Short upload hue.\n"
                    + "\n".join(errors[-3:]) + "\nGitHub > Actions mein log dekh.")
    if not made:
        sys.exit(1)                       # already alerted above


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


def run_photos():
    st = state.load()
    try:
        photos.run(st)
    except Exception as e:
        traceback.print_exc()
        # alert once per kind of problem, not every week
        msg = f"{type(e).__name__}: {str(e)[:200]}"
        if st.get("photo_agent_error") != msg[:80]:
            notify.send(f"⚠️ {CHANNEL_NAME}: photo agent naye photos nahi bana paya ({msg}). "
                        "Purane photos se videos chalti rahengi.")
        st["photo_agent_error"] = msg[:80]
    else:
        st.pop("photo_agent_error", None)
    state.save(st)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("task", choices=["daily", "comments", "photos"])
    p.add_argument("--count", type=int, default=SCRIPTS_PER_DAY)
    p.add_argument("--no-upload", action="store_true")
    a = p.parse_args(argv)
    try:
        if a.task == "daily":
            run_daily(max(1, a.count), not a.no_upload)
        elif a.task == "photos":
            run_photos()
        else:
            run_comments()
    except Exception as e:
        notify.send(f"⚠️ {CHANNEL_NAME} {a.task} FAILED: {type(e).__name__}: {str(e)[:300]}")
        raise


if __name__ == "__main__":
    sys.exit(main())
