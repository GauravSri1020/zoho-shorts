"""Manual Gemini mode: YOU make the avatar clips in the Gemini app (free with your Pro plan), the robot does the rest.

  channel.yaml -> avatar.engine: "gemini_manual"

1. prepare (10:00 IST, the normal daily run): research -> script -> QA -> voice, exactly as before. Instead of
   rendering, it saves a job folder in the repo:
       jobs/<id>/PROMPTS.md   <- open this: one prompt per clip, copy-paste into Gemini with your photo
       jobs/<id>/job.json     <- script, timings (the robot's notes)
       jobs/<id>/voice.wav    <- the AI voice of this Short
   and sends you the link on Telegram.
2. You: Gemini app -> upload your photo -> paste prompt 1 -> download the video. Same for prompt 2, 3...
   Then on GitHub open jobs/<id>/clips/ ("Add file > Upload files") and upload them in order
   (01.mp4, 02.mp4, ... - or just upload them in the same order; files are sorted by name).
3. assemble (starts by itself when clips are uploaded): Gemini's audio is thrown away, every clip is
   re-timed word by word onto the AI voice (veo.assemble), then the normal composer makes the Short
   (Zoho screens, captions, music, layout - unchanged) -> QA agent -> scheduled YouTube upload.
   The job folder is deleted after the upload.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import traceback
from pathlib import Path

from .config import CH, CHANNEL_NAME, MAX_VIDEO_SECONDS, OUT_DIR, ROOT

JOBS = ROOT / "jobs"
_M = (CH.get("avatar", {}) or {}).get("manual", {}) or {}
MAX_CLIPS = int(_M.get("max_clips", 3))          # Gemini Pro gives ~3 video generations a day
PER_DAY = int(_M.get("per_day", 1))
VIDEO_EXT = (".mp4", ".mov", ".webm", ".m4v")
REPO = os.getenv("GITHUB_REPOSITORY", "GauravSri1020/zoho-shorts")


def _link(path):
    return f"https://github.com/{REPO}/blob/main/{path}"


def _upload_link(job_id):
    return f"https://github.com/{REPO}/upload/main/jobs/{job_id}/clips"


def _prompts_md(job):
    from . import veo
    rows = []
    for i, p in enumerate(job["clips"]):
        rows += [f"## Clip {i + 1:02d}  ->  upload as **{i + 1:02d}.mp4**", "",
                 f"Line: **{p['text']}**", "", "Prompt (copy this):", "", "    " + veo._prompt(p["text"]), ""]
    return "\n".join([
        f"# {job['title']}", "",
        f"Short id: **{job['id']}** · {len(job['clips'])} clip(s) · made {job['created'][:16]}", "",
        "## Kya karna hai", "",
        "1. Gemini app kholo (gemini.google.com) -> **Video** (Veo) chuno.",
        "2. Apni ek clear photo upload karo (chehra saaf, camera ki taraf). Har clip mein **same photo** use karo.",
        "3. Neeche ka Clip 01 prompt copy karke paste karo -> video download karo. Phir Clip 02, 03...",
        f"4. Saare clips yahan upload karo: **{_upload_link(job['id'])}**",
        "   (naam 01.mp4, 02.mp4 ... rakho, ya isi order mein upload karo). Commit changes dabao.",
        "5. Bas. Robot khud jod ke video banayega, QA karega aur YouTube pe schedule karega.",
        "", "Gemini ki awaaz hata di jaati hai - video mein wahi AI voice rahegi, lips us pe fit kar diye jaate hain.",
        "", *rows])


def prepare(count, do_upload):
    """Daily run in manual mode: scripts + voice + prompts, no rendering."""
    from . import editor, notify, research, state, voice, writer, veo
    from .main import _lines, build_description, build_title
    count = max(1, min(count, PER_DAY))
    st = state.load()
    candidates = research.fetch(st["covered_links"])
    angles = writer.scout(candidates, count + 2, st["problems"])
    made, errors = 0, []
    for k, angle in enumerate(angles):
        if made >= count:
            break
        job_id = f"{dt.datetime.utcnow():%Y%m%d-%H%M}-{k + 1}"
        work = OUT_DIR / job_id
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        print(f"\n[manual] === {angle.get('problem')}")
        try:
            sc = writer.approved_script(angle)
            lines = _lines(sc)
            wav, _ = voice.synthesize(lines, work / "voice", MAX_VIDEO_SECONDS)
            script_text = " ".join(voice._clean(l.get("say") or l.get("tts")) for l in lines)
            words = editor.align_to_script(editor.transcribe(wav, work), script_text, wav)
            dur = voice.duration(wav)
            plist = veo.pieces(lines, words, dur)
            if not plist:
                raise RuntimeError("script has no on-camera line")
            # Gemini clips go to the hook + the longest other on-camera lines; the rest reuse them
            order = [0] + sorted(range(1, len(plist)), key=lambda i: plist[i]["t1"] - plist[i]["t0"], reverse=True)
            clips = [{"piece": i, "text": plist[i]["text"]} for i in sorted(order[:MAX_CLIPS])]
            d = JOBS / job_id
            (d / "clips").mkdir(parents=True, exist_ok=True)
            (d / "clips" / ".keep").write_text("upload the Gemini clips here\n")
            shutil.copy(wav, d / "voice.wav")
            job = {"id": job_id, "status": "waiting_for_clips", "upload": do_upload,
                   "created": dt.datetime.utcnow().isoformat(timespec="seconds"),
                   "title": build_title(sc), "description": build_description(sc, angle),
                   "angle": {k2: v for k2, v in angle.items() if k2 != "story"}, "story": angle.get("story"),
                   "script": sc, "lines": lines, "words": words, "dur": dur, "pieces": plist,
                   "clips": clips}
            (d / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "PROMPTS.md").write_text(_prompts_md(job), encoding="utf-8")
            st["problems"].append(angle["problem"])
            if angle.get("story"):
                st["covered_links"].append(angle["story"]["link"])
            st["scripts"][f"S{st['next_id']:04d}"] = {"problem": angle["problem"], "title": job["title"],
                                                      "engine": "gemini_manual", "job": job_id,
                                                      "created": job["created"]}
            st["next_id"] += 1
            made += 1
            notify.send(f"🎬 {CHANNEL_NAME}: naya Short ready - {len(clips)} Gemini clip(s) chahiye.\n"
                        f"Prompts: {_link(f'jobs/{job_id}/PROMPTS.md')}\nUpload: {_upload_link(job_id)}")
            print(f"[manual] job {job_id}: {len(clips)} clips -> {_link(f'jobs/{job_id}/PROMPTS.md')}")
        except Exception as e:
            traceback.print_exc()
            errors.append(f"{angle.get('problem', '')[:60]}: {type(e).__name__}: {str(e)[:200]}")
        finally:
            state.save(st)
    if not made:
        raise RuntimeError("no Short prepared: " + "; ".join(errors[-3:]))


def _clip_files(d: Path):
    return sorted(p for p in (d / "clips").iterdir() if p.suffix.lower() in VIDEO_EXT)


def _first_frame(clip, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.1", "-i", str(clip), "-frames:v", "1",
                    "-q:v", "2", str(out)], check=True)
    return out


def finish():
    """Assembles every job whose clips are uploaded. Returns number of Shorts finished."""
    from . import benchmark, composer, editor, google_apis as g, notify, schedule, state, veo
    jobs = sorted(JOBS.glob("*/job.json")) if JOBS.exists() else []
    done = 0
    for jf in jobs:
        d = jf.parent
        job = json.loads(jf.read_text(encoding="utf-8"))
        files = _clip_files(d)
        need = len(job["clips"])
        if len(files) < need:
            print(f"[manual] {job['id']}: {len(files)}/{need} clips uploaded, waiting")
            continue
        files = files[:need]
        work = OUT_DIR / job["id"]
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        print(f"\n[manual] === assembling {job['id']} from {[f.name for f in files]}")
        try:
            plist = job["pieces"]
            for p in plist:
                p["words"] = [tuple(w) for w in p["words"]]
            # each clip belongs to one line; lines without their own clip reuse the clips in turn
            own = {c.get("piece", n): n for n, c in enumerate(job["clips"])}
            clips = [files[own[i]] if i in own else files[i % need] for i in range(len(plist))]
            for i, p in enumerate(plist):
                p["reuse"] = i not in own
            words = [tuple(w) for w in job["words"]]
            frame = _first_frame(files[0], work / "first_frame.jpg")
            (work / "avatar").mkdir(parents=True, exist_ok=True)
            av = veo.assemble(frame, plist, clips, job["dur"], work / "avatar", work / "avatar.mp4")
            mp4 = work / "short.mp4"
            sc = job["script"]
            composer.render(sc, job["lines"], words, av, d / "voice.wav", work / "edit", mp4)
            try:
                benchmark.learn(g.youtube())
            except Exception as e:
                print(f"[benchmark] learn skipped: {str(e)[:200]}")
            problems = editor.check_media(mp4)
            report = benchmark.gate(mp4, sc, "veo", problems)
            (work / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[qa] score={report['overall']}/{report['min_score']} approved={report['approved']}")
            if not report["approved"]:
                for f in files:                            # rejected clips are removed, upload new ones
                    f.unlink()
                notify.send(f"⚠️ {CHANNEL_NAME}: Short {job['id']} QA mein fail ({report['overall']}/"
                            f"{report['min_score']}).\n" + "\n".join(map(str, report["issues"][:4])) +
                            f"\nNaye clips yahan daal: {_upload_link(job['id'])}")
                continue
            st = state.load()
            if job.get("upload", True):
                yt = g.youtube()
                when, slot = schedule.next_slot(st["slots"])
                tags = list(sc.get("tags") or []) + ["Zoho", "Shorts"]
                vid = g.upload(yt, mp4, job["title"], job["description"], tags, schedule.to_rfc3339_utc(when))
                st["slots"].append(slot | {"video_id": vid, "title": job["title"]})
                for v in st["scripts"].values():
                    if v.get("job") == job["id"]:
                        v |= {"video_id": vid, "publish_at": when.isoformat()}
                print(f"[manual] scheduled for {when:%d %b %I:%M %p} IST: https://youtube.com/shorts/{vid}")
            state.save(st)
            (work / "short.json").write_text(json.dumps({k: job[k] for k in ("title", "description", "script")},
                                                        ensure_ascii=False, indent=1), encoding="utf-8")
            shutil.rmtree(d)                               # job done -> remove it from the repo
            done += 1
        except Exception as e:
            traceback.print_exc()
            notify.send(f"⚠️ {CHANNEL_NAME}: Short {job['id']} jod nahi paya: {type(e).__name__}: {str(e)[:200]}")
        finally:
            shutil.rmtree(work / "edit", ignore_errors=True)
    print(f"[manual] {done} Short(s) finished")
    return done
