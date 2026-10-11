"""Flow mode - the presenter is YOU, made in Google Flow (your avatar + Veo 3.1 with its own voice).

Every day (10:00 IST, task "daily"):
  research -> script -> QA (unchanged) -> the script is cut into short clips (1-2 lines, max ~7 s each) ->
  jobs/<id>/job.json + jobs/<id>/PROMPTS.md -> a GitHub Issue "Today's Short" with every prompt in a copy box
  and the upload link. GitHub e-mails you that issue (you are assigned to it).
You (about 5 min):
  flow.google.com -> your avatar, 9:16 -> paste prompt 1 -> download, prompt 2 -> download ... ->
  open the upload link -> drag ALL clips in (any names, any order) -> Commit changes.
Robot (task "assemble", starts by itself when the clips are uploaded):
  whisper listens to every clip and matches it to its prompt (file names / order do not matter) ->
  silence at the start and end is cut, the Flow watermark is hidden (crop or blur) -> clips joined.
  Flow's own voice is KEPT, so the lips always match -> word timings -> composer (Zoho screens, captions,
  music, layout - unchanged) -> QA agent -> scheduled YouTube upload -> issue closed, job folder removed.
"""
import datetime as dt
import difflib
import json
import os
import re
import shutil
import subprocess
import traceback
import urllib.request
from pathlib import Path

from .config import CH, CHANNEL_NAME, OUT_DIR, ROOT

JOBS = ROOT / "jobs"
_F = CH.get("flow", {}) or {}
PER_DAY = int(_F.get("per_day", 1))
MAX_WORDS = int(_F.get("max_words_per_clip", 17))     # ~7 s of speech -> fits one 8 s Flow clip
PRESENTER = (_F.get("presenter") or "The man").strip()
SCENE = (_F.get("scene") or "").strip()
_WM = _F.get("watermark", {}) or {}
WM_MODE = str(_WM.get("mode", "crop")).lower()          # crop | blur | none
WM_CROP = float(_WM.get("crop_bottom", 0.10))
WM_BOX = [float(v) for v in (_WM.get("box") or [0.74, 0.88, 0.24, 0.10])]   # x, y, w, h (fractions)
VIDEO_EXT = (".mp4", ".mov", ".webm", ".m4v")
REPO = os.getenv("GITHUB_REPOSITORY", "GauravSri1020/zoho-shorts")
W, H, FPS, RATE = 720, 1280, 30, 44100


def _run(cmd):
    subprocess.run(cmd, check=True)


def _ff(*a):
    return ["ffmpeg", "-y", "-loglevel", "error", *a]


def _dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True, check=True).stdout.strip())


def _size(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0:s=x", str(p)],
                         capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split("\n")[0].split("x")[:2]
    return int(w), int(h)


def _has_audio(p):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def _clean(t):
    return re.sub(r"\s+", " ", re.sub(r"[\[<][^\]>]{1,30}[\]>]", "", t or "")).strip()


def _say(line):
    return _clean(line.get("say") or line.get("tts"))


# ------------------------------------------------------------------ script -> Flow clips
def chunks(lines):
    """Consecutive script lines packed into clips of <= MAX_WORDS words; long lines are split.
    Returns [{"text", "lines": [line indexes], "beat"}] in script order."""
    out, cur, idx = [], [], []

    def flush():
        if cur:
            out.append({"text": " ".join(cur), "lines": sorted(set(idx)),
                        "beat": str(lines[idx[0]].get("beat", ""))})
            cur.clear()
            idx.clear()

    for i, l in enumerate(lines):
        words = _say(l).split()
        if not words:
            continue
        if len(words) > MAX_WORDS:                       # one long line -> several equal parts
            flush()
            parts = -(-len(words) // MAX_WORDS)
            size = -(-len(words) // parts)
            for j in range(0, len(words), size):
                cur.extend(words[j:j + size])
                idx.append(i)
                flush()
            continue
        solo = str(l.get("beat", "")).upper().startswith(("HOOK", "CTA"))   # hook / CTA: own clip
        if cur and (solo or len(cur) + len(words) > MAX_WORDS or
                    str(lines[idx[0]].get("beat", "")).upper().startswith(("HOOK", "CTA"))):
            flush()
        cur.extend(words)
        idx.append(i)
    flush()
    return out


_ACT = {"HOOK": "leans in slightly with an energetic, curious expression",
        "PROBLEM": "frowns a little and gestures with one open hand, showing the frustration",
        "FIX": "nods confidently and counts on his fingers",
        "STEP": "points to the side as if showing something on a screen next to him",
        "RESULT": "smiles and opens both hands",
        "CTA": "smiles warmly and points at the camera"}


def prompt(text, beat=""):
    b = str(beat).upper()
    act = next((v for k, v in _ACT.items() if b.startswith(k)), "explains calmly with small natural hand gestures")
    return (f"{PRESENTER} looks straight into the camera and talks to the viewer like a friendly YouTube tech "
            f"explainer; he {act}. Vertical 9:16 medium close-up, static camera, face sharp and well lit"
            + (f", {SCENE}" if SCENE else "") + ". "
            f"He says, in clear natural English with an Indian accent: \"{text}\" "
            "His lips match every word. He starts speaking immediately and stops right after the last word. "
            "Audio: only his voice - no music, no sound effects. No subtitles, no captions, no text on screen.")


# ------------------------------------------------------------------ GitHub issue = your daily "screen"
def _gh(method, path, body=None):
    tok = os.getenv("GITHUB_TOKEN", "").strip()
    if not tok:
        print(f"[flow] no GITHUB_TOKEN - skipped GitHub {method} {path}")
        return {}
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}{path}", method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except Exception as e:
        print(f"[flow] GitHub {method} {path} failed: {str(e)[:200]}")
        return {}


def _comment(job, text):
    if job.get("issue"):
        _gh("POST", f"/issues/{job['issue']}/comments", {"body": text})


def upload_link(job_id):
    return f"https://github.com/{REPO}/upload/main/jobs/{job_id}/clips"


def _body(job):
    n = len(job["clips"])
    rows = []
    for i, c in enumerate(job["clips"]):
        rows += [f"### Clip {i + 1} of {n}", "", f"> {c['text']}", "", "```text", c["prompt"], "```", ""]
    return "\n".join([
        f"## 🎬 {job['title']}", "",
        f"**{n} Flow clips** · Short `{job['id']}` · {job['created'][:10]}", "",
        "### Steps (about 5 min)",
        "1. Open **https://flow.google.com** -> your project -> video settings **9:16**, model **Veo 3.1 - Fast**.",
        "2. Select **your avatar** (Characters), so every clip is you with your voice.",
        "3. For each box below: click the copy button (top-right of the box) -> paste in Flow -> generate -> "
        "**Download** the video.",
        f"4. Open **[this upload link]({upload_link(job['id'])})** -> drag **all** the clips in -> **Commit changes**.",
        "   Any file names, any order: the robot listens to every clip and matches it to its line.",
        "5. Done. The robot cuts, joins, hides the Flow watermark, adds Zoho screens + captions + music, checks the "
        "quality and schedules it on YouTube. This issue closes by itself.", "",
        "Retake a bad clip? Just upload the new one too - the clip that matches its line best is used.",
        "", "---", "", *rows])


def prepare(count, do_upload):
    """Daily run: research -> script -> clip prompts -> job folder + GitHub issue. Nothing is rendered."""
    from . import notify, research, state, writer
    from .main import _lines, build_description, build_title
    count = max(1, min(count, PER_DAY))
    st = state.load()
    angles = writer.scout(research.fetch(st["covered_links"]), count + 2, st["problems"])
    print(f"[flow] scout found {len(angles)} angles")
    made, errors = 0, []
    for k, angle in enumerate(angles):
        if made >= count:
            break
        job_id = f"{dt.datetime.utcnow():%Y%m%d-%H%M}-{k + 1}"
        print(f"\n[flow] === {angle.get('problem')}")
        try:
            sc = writer.approved_script(angle)
            lines = _lines(sc)
            clips = chunks(lines)
            if not clips:
                raise RuntimeError("script has no spoken lines")
            for c in clips:
                c["prompt"] = prompt(c["text"], c["beat"])
            d = JOBS / job_id
            (d / "clips").mkdir(parents=True, exist_ok=True)
            (d / "clips" / ".keep").write_text("drop the Flow clips here\n")
            job = {"id": job_id, "status": "waiting_for_clips", "upload": do_upload,
                   "created": dt.datetime.utcnow().isoformat(timespec="seconds"),
                   "title": build_title(sc), "description": build_description(sc, angle),
                   "angle": {k2: v for k2, v in angle.items() if k2 != "story"}, "story": angle.get("story"),
                   "script": sc, "lines": lines, "clips": clips}
            body = _body(job)
            issue = _gh("POST", "/issues", {"title": f"🎬 Today's Short: {job['title'][:70]} ({len(clips)} Flow clips)",
                                            "body": body, "assignees": [REPO.split("/")[0]]})
            job["issue"] = issue.get("number")
            (d / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "PROMPTS.md").write_text(body, encoding="utf-8")
            st["problems"].append(angle["problem"])
            if angle.get("story"):
                st["covered_links"].append(angle["story"]["link"])
            st["scripts"][f"S{st['next_id']:04d}"] = {"problem": angle["problem"], "title": job["title"],
                                                      "engine": "flow", "job": job_id, "created": job["created"]}
            st["next_id"] += 1
            made += 1
            where = issue.get("html_url") or f"https://github.com/{REPO}/blob/main/jobs/{job_id}/PROMPTS.md"
            notify.send(f"🎬 {CHANNEL_NAME}: today's Short needs {len(clips)} Flow clips.\n"
                        f"Prompts: {where}\nUpload: {upload_link(job_id)}")
            print(f"[flow] job {job_id}: {len(clips)} clips -> {where}")
        except Exception as e:
            traceback.print_exc()
            errors.append(f"{angle.get('problem', '')[:60]}: {type(e).__name__}: {str(e)[:200]}")
        finally:
            state.save(st)
    if not made:
        raise RuntimeError("no Short prepared: " + "; ".join(errors[-3:]))


# ------------------------------------------------------------------ clips -> finished Short
def _clip_files(d: Path):
    c = d / "clips"
    return sorted(p for p in c.iterdir() if p.suffix.lower() in VIDEO_EXT) if c.exists() else []


def _words(t):
    return re.findall(r"[a-z0-9]+", (t or "").lower())


def match(files, clips, work: Path):
    """Which uploaded file is which clip: whisper hears each file, best text match wins.
    Returns ({clip index: (file index, score)}, [heard words per file])."""
    from . import editor
    heard = []
    for n, f in enumerate(files):
        if not _has_audio(f):
            raise RuntimeError(f"{f.name} has no sound - download the Flow clip as a video WITH audio")
        wd = work / f"hear{n:02d}"
        wd.mkdir(parents=True, exist_ok=True)
        heard.append(editor.transcribe(f, wd))
    scores = sorted(((difflib.SequenceMatcher(None, _words(" ".join(w[2] for w in heard[fi])),
                                               _words(c["text"])).ratio(), fi, ci)
                     for fi in range(len(files)) for ci, c in enumerate(clips)), reverse=True)
    pick, used = {}, set()
    for s, fi, ci in scores:
        if ci not in pick and fi not in used:
            pick[ci] = (fi, s)
            used.add(fi)
    return pick, heard


def _hide_watermark(vf_in, size):
    if WM_MODE == "crop" and WM_CROP > 0:
        return f"{vf_in}crop=iw:trunc(ih*{1 - WM_CROP:.3f}/2)*2:0:0[c]", "[c]"
    if WM_MODE == "blur":
        w, h = size
        x, y, bw, bh = WM_BOX
        bx, by = int(w * x) // 2 * 2, int(h * y) // 2 * 2
        bw, bh = max(int(w * bw) // 2 * 2, 8), max(int(h * bh) // 2 * 2, 8)
        bw, bh = min(bw, w - bx), min(bh, h - by)
        return (f"{vf_in}split[a][b];[b]crop={bw}:{bh}:{bx}:{by},boxblur=18:3[bl];"
                f"[a][bl]overlay={bx}:{by}[c]"), "[c]"
    return f"{vf_in}null[c]", "[c]"


def prep_clip(src: Path, heard, out_v: Path, out_a: Path):
    """One clip: speech only (silence at both ends cut), watermark hidden, 720x1280 @30, wav 44.1 kHz.
    Video and audio get exactly the same length, so lips never drift when clips are joined."""
    from . import editor
    d = _dur(src)
    if heard:
        a, b = heard[0][0] - 0.12, heard[-1][1] + 0.30
    else:
        sp = editor.speech_spans(src)
        a, b = sp[0][0] - 0.10, sp[-1][1] + 0.25
    a, b = max(0.0, a), min(d, b)
    if b - a < 0.6:
        a, b = 0.0, d
    frames = max(int(round((b - a) * FPS)), 1)
    length = frames / FPS
    chain, last = _hide_watermark("[0:v]", _size(src))
    fc = (f"{chain};{last}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"fps={FPS},setsar=1,format=yuv420p[v]")
    _run(_ff("-ss", f"{a:.3f}", "-i", str(src), "-filter_complex", fc, "-map", "[v]", "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-r", str(FPS), str(out_v)))
    _run(_ff("-ss", f"{a:.3f}", "-i", str(src), "-vn", "-ac", "1", "-ar", str(RATE), "-af",
             f"apad=whole_dur={length:.3f}", "-t", f"{length:.3f}", "-c:a", "pcm_s16le", str(out_a)))
    return length


def join(parts, work: Path):
    """[(video, wav)] -> (avatar.mp4, voice.wav)"""
    vl, al = work / "v.txt", work / "a.txt"
    vl.write_text("".join(f"file '{v.resolve()}'\n" for v, _ in parts))
    al.write_text("".join(f"file '{a.resolve()}'\n" for _, a in parts))
    av, raw, voice = work / "avatar.mp4", work / "voice_raw.wav", work / "voice.wav"
    _run(_ff("-f", "concat", "-safe", "0", "-i", str(vl), "-c", "copy", str(av)))
    _run(_ff("-f", "concat", "-safe", "0", "-i", str(al), "-c", "copy", str(raw)))
    _run(_ff("-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(RATE), "-ac", "1", str(voice)))
    return av, voice


def build(job, files, work: Path):
    """Clips -> finished Short (short.mp4). Returns (mp4, report-notes)."""
    from . import composer, editor
    clips = job["clips"]
    pick, heard = match(files, clips, work)
    missing = [i + 1 for i in range(len(clips)) if i not in pick]
    if missing:
        raise RuntimeError(f"no uploaded clip for clip(s) {missing}")
    notes = []
    for i in range(len(clips)):
        fi, s = pick[i]
        print(f"[flow] clip {i + 1} <- {files[fi].name} (text match {s:.2f})")
        if s < 0.45:
            notes.append(f"clip {i + 1} ({files[fi].name}) does not say its line well (match {s:.2f})")
    parts = []
    for i in range(len(clips)):
        fi, _ = pick[i]
        v, a = work / f"p{i:02d}.mp4", work / f"p{i:02d}.wav"
        prep_clip(files[fi], heard[fi], v, a)
        parts.append((v, a))
    av, voice = join(parts, work)
    script_text = " ".join(c["text"] for c in clips)
    words = editor.align_to_script(editor.transcribe(voice, work), script_text, voice)
    mp4 = work / "short.mp4"
    composer.render(job["script"], job["lines"], words, av, voice, work / "edit", mp4)
    return mp4, notes


def finish():
    """Assembles every job whose clips are all uploaded. Returns the number of Shorts finished."""
    from . import benchmark, editor, google_apis as g, notify, schedule, state
    jobs = sorted(JOBS.glob("*/job.json")) if JOBS.exists() else []
    done = 0
    for jf in jobs:
        d = jf.parent
        job = json.loads(jf.read_text(encoding="utf-8"))
        files = _clip_files(d)
        need = len(job["clips"])
        if len(files) < need:
            print(f"[flow] {job['id']}: {len(files)}/{need} clips uploaded, waiting")
            continue
        work = OUT_DIR / job["id"]
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        print(f"\n[flow] === assembling {job['id']} from {[f.name for f in files]}")
        try:
            mp4, notes = build(job, files, work)
            try:
                benchmark.learn(g.youtube())
            except Exception as e:
                print(f"[benchmark] learn skipped: {str(e)[:200]}")
            sc = job["script"]
            report = benchmark.gate(mp4, sc, "flow", editor.check_media(mp4) + notes)
            (work / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[qa] score={report['overall']}/{report['min_score']} approved={report['approved']}")
            (work / "short.json").write_text(json.dumps({k: job[k] for k in ("title", "description", "script")},
                                                        ensure_ascii=False, indent=1), encoding="utf-8")
            run_link = (f"https://github.com/{REPO}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
                        if os.getenv("GITHUB_RUN_ID") else "")
            if not report["approved"]:
                issues = "\n".join(f"- {x}" for x in map(str, report["issues"][:6]))
                _comment(job, f"⚠️ QA failed ({report['overall']}/{report['min_score']}):\n{issues}\n\n"
                              f"Video to check: {run_link} (Artifacts). Upload retakes of the bad clips here: "
                              f"{upload_link(job['id'])}")
                notify.send(f"⚠️ {CHANNEL_NAME}: Short {job['id']} failed QA ({report['overall']}/"
                            f"{report['min_score']}).\n{issues}\nRetakes: {upload_link(job['id'])}")
                continue
            st = state.load()
            msg = f"✅ Short ready. Video: {run_link} (Artifacts)."
            if job.get("upload", True):
                yt = g.youtube()
                when, slot = schedule.next_slot(st["slots"])
                tags = list(sc.get("tags") or []) + ["Zoho", "Shorts"]
                vid = g.upload(yt, mp4, job["title"], job["description"], tags, schedule.to_rfc3339_utc(when))
                st["slots"].append(slot | {"video_id": vid, "title": job["title"]})
                for v in st["scripts"].values():
                    if v.get("job") == job["id"]:
                        v |= {"video_id": vid, "publish_at": when.isoformat()}
                msg = (f"✅ Scheduled for {when:%d %b %I:%M %p} IST: https://youtube.com/shorts/{vid}\n"
                       f"Video file: {run_link} (Artifacts).")
                print(f"[flow] scheduled for {when:%d %b %I:%M %p} IST: https://youtube.com/shorts/{vid}")
            state.save(st)
            _comment(job, msg)
            if job.get("issue"):
                _gh("PATCH", f"/issues/{job['issue']}", {"state": "closed"})
            shutil.rmtree(d)                      # job done -> its folder (and clips) leave the repo
            done += 1
        except Exception as e:
            traceback.print_exc()
            _comment(job, f"⚠️ Could not build the Short: {type(e).__name__}: {str(e)[:300]}")
            notify.send(f"⚠️ {CHANNEL_NAME}: Short {job['id']} failed: {type(e).__name__}: {str(e)[:200]}")
        finally:
            shutil.rmtree(work / "edit", ignore_errors=True)
    print(f"[flow] {done} Short(s) finished")
    return done
