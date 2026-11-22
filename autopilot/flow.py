"""Flow mode - the presenter is YOU, made in Google Flow (your avatar + Veo 3.1 with its own voice).

Every day (10:00 IST, task "daily"):
  research -> script -> QA (unchanged) -> the script is cut into short clips (1-2 lines, max ~7 s each) ->
  jobs/<id>/job.json + jobs/<id>/PROMPTS.md -> a GitHub Issue "Today's Short" with every prompt in a copy box
  and the upload link. GitHub e-mails you that issue (you are assigned to it).
You (or Claude in the browser, about 5 min):
  flow.google.com -> your avatar, 9:16 -> paste the prompts -> download -> open the upload link ->
  drag ALL clips in (any names, any order) -> Commit changes.
Robot (task "assemble", starts by itself when the clips are uploaded):
  whisper listens to every clip and matches it to its prompt (file names / order do not matter) ->
  silence at the start and end is cut tight, the pace is lifted a little (flow.speed), the Flow watermark is
  hidden (crop or blur) -> clips joined. Flow's own voice is KEPT, so the lips always match -> word timings ->
  composer (full-screen presenter + Zoho screens, captions, music) -> QA agent -> scheduled YouTube upload
  (title + description also in the channel.yaml -> localize languages) -> issue closed, job folder removed.
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

from .config import CH, CHANNEL_NAME, OUT_DIR, ROOT, LOCALES, IS_ZOHO, NICHE_ID

JOBS = ROOT / "jobs"
_F = CH.get("flow", {}) or {}
PER_DAY = int(_F.get("per_day", 1))
MAX_BATCH = int(_F.get("max_batch", 14))  # a manual "daily" run may prepare a whole week at once
MAX_WORDS = int(_F.get("max_words_per_clip", 19))  # ~7.5 s of speech -> fits one 8 s Flow clip
PRESENTER = (_F.get("presenter") or "The man").strip()
SCENE = (_F.get("scene") or "").strip()
ACCENT = (_F.get("accent") or "a clear, neutral international accent").strip()
SHOT = (_F.get("shot") or "Vertical 9:16 medium-wide shot from the knees up, camera about two metres away, "
        "his head in the upper third with space above it, both hands and all his gestures fully visible in the "
        "frame").strip()
LOOKS = [str(x).strip() for x in (_F.get("looks") or []) if str(x).strip()] or [SCENE]  # one look per Short, rotated
_LK = _F.get("look_parts") or {}
GARMENTS = [str(x).strip() for x in (_LK.get("garments") or []) if str(x).strip()]
COLOURS = [str(x).strip() for x in (_LK.get("colours") or []) if str(x).strip()]
PLACES = [x if isinstance(x, dict) else {"text": str(x)} for x in (_LK.get("places") or []) if x]
BEARDS = [str(x).strip() for x in (_LK.get("beards") or []) if str(x).strip()]
HAIRS = [str(x).strip() for x in (_LK.get("hair") or []) if str(x).strip()]
EYEWEAR = [str(x).strip() for x in (_LK.get("eyewear") or []) if str(x).strip()]
SUNGLASSES = [str(x).strip() for x in (_LK.get("sunglasses") or []) if str(x).strip()]
OUTFITS = [str(x).strip() for x in (_F.get("outfits") or []) if str(x).strip()]  # old fixed list (fallback only)


def pick_look(st):
    """11 Nov 2026 (Gaurav): every Short gets its OWN look and nothing is ever reused:
    - outfit = colour x garment, never worn before (state used_outfits)
    - place never used again until every place was used once (state used_places)
    - beard / hair / glasses (sunglasses only outdoors) change every Short, never the same mix as the Short before
    The look is written ONCE per Short and goes into every clip's prompt -> identical in every shot of that Short.
    Without look_parts in the niche file: the old rotation through "looks"."""
    import hashlib
    if not (GARMENTS and COLOURS and PLACES):
        return LOOKS[st.get("look_index", 0) % len(LOOKS)]
    rnd = int(hashlib.md5(str(st.get("next_id", 0)).encode()).hexdigest()[:12], 16)
    # outfit: a colour x garment combination never worn
    worn = set(st.setdefault("used_outfits", []))
    fits = [f"{c} {g}" for g in GARMENTS for c in COLOURS if f"{c} {g}" not in worn]
    last = st["used_outfits"][-1] if st["used_outfits"] else ""
    fresh = [f for f in fits if not any(w in last for w in f.split()[-2:])] or fits  # not the same garment twice
    if not fresh:
        st["used_outfits"], fresh = [], [f"{c} {g}" for g in GARMENTS for c in COLOURS]
    outfit = fresh[rnd % len(fresh)]
    st["used_outfits"].append(outfit)
    # place: not used again until all were used
    used_p = st.setdefault("used_places", [])
    free = [i for i in range(len(PLACES)) if i not in used_p] or list(range(len(PLACES)))
    if len(free) == len(PLACES):
        used_p.clear()
    pi = free[(rnd // 7) % len(free)]
    used_p.append(pi)
    place = PLACES[pi]
    outdoor = bool(place.get("outdoor"))
    # grooming: beard x hair x glasses, never the same mix as the Short before
    prev = st.get("last_grooming") or []
    mixes = [(b, h, e) for b in range(len(BEARDS) or 1) for h in range(len(HAIRS) or 1)
             for e in range(len(EYEWEAR) + (len(SUNGLASSES) if outdoor else 0) or 1)
             if [b, h, e] != prev and (not prev or (b != prev[0] and h != prev[1]))]
    b, h, e = mixes[(rnd // 31) % len(mixes)]
    st["last_grooming"] = [b, h, e]
    glasses = (EYEWEAR + (SUNGLASSES if outdoor else []))[e] if (EYEWEAR or SUNGLASSES) else ""
    groom = ", ".join(x for x in ((BEARDS[b] if BEARDS else ""), (HAIRS[h] if HAIRS else ""), glasses) if x)
    return (f"wearing {outfit}, {place['text']}; in this whole video he has {groom} - exactly the same in every "
            f"shot of this video")
SPEED = max(1.0, min(1.6, float(_F.get("speed", 1.1))))  # lifts Veo's slow delivery (voice + lips together); v2 claude niche 1.5
# screen-part (TTS) voice pace. 1.0 = untouched (Zoho niche). Claude niche v2: same as SPEED, so the pace never jumps.
TTS_SPEED = max(1.0, min(1.6, float(_F.get("tts_speed", 1.0))))
LEAD, TAIL = float(_F.get("lead_seconds", 0.04)), float(_F.get("tail_seconds", 0.18))
_WM = _F.get("watermark", {}) or {}
WM_MODE = str(_WM.get("mode", "crop")).lower()  # crop | blur | none
WM_CROP = float(_WM.get("crop_bottom", 0.10))
WM_BOX = [float(v) for v in (_WM.get("box") or [0.74, 0.88, 0.24, 0.10])]  # x, y, w, h (fractions)
VIDEO_EXT = (".mp4", ".mov", ".webm", ".m4v")
REPO = os.getenv("GITHUB_REPOSITORY", "GauravSri1020/zoho-shorts")
W, H, FPS, RATE = 720, 1280, 30, 44100
SKIP_STATUS = ("done", "uploaded", "uploaded_manually", "skip", "skip_no_clips")
# Your face (Flow clips) only where it matters; everything else is the Zoho screen with the same voice (tts.py).
FACE_BEATS = tuple(str(b).upper() for b in (_F.get("face_beats") or ["HOOK", "PROBLEM", "RESULT"]))
# v4 (1 Nov 2026): faceless Shorts - no Flow clip at all (every line = screen + one TTS voice), so the robot can publish
# every day with zero Flow credits. Env FACE=yes (Run workflow -> face) makes a Short with the face clip(s) again.
# 11 Nov 2026: Zoho default = AVATAR Shorts again (Claude makes the Flow clips when Gaurav opens the Flow tab);
# FACE=no forces faceless, FACE=yes forces avatar; a Short whose clips never came is built faceless by fallback().
_FACE = os.getenv("FACE", "").strip().lower()
FACELESS = (_FACE in ("no", "0", "false", "n", "faceless")
            or (bool(_F.get("faceless")) and _FACE not in ("1", "yes", "true", "y")))
# 22 Nov 2026 (Gaurav): Zoho Shorts are NEVER faceless - Flow (HOOK + PROBLEM) -> real Zoho screens -> Flow (RESULT).
NEVER_FACELESS = bool(_F.get("never_faceless")) and IS_ZOHO
if NEVER_FACELESS and FACELESS:
    print("[flow] never_faceless: FACE=no / faceless ignored - Zoho Shorts always get the Flow clips")
    FACELESS = False
EXPIRE_HOURS = float(_F.get("expire_hours", 30))
EXTRA_ANGLES = int(_F.get("extra_angles", 2))
if FACELESS:
    FACE_BEATS = ()
DROP_BEATS = tuple(str(b).upper() for b in (_F.get("drop_beats") or ["CTA"]))
MAX_WAITING = int(_F.get("max_waiting", 2))  # the scheduled daily run skips if this many Shorts still wait for clips
# NICHE SWITCH (27 Oct 2026): words that differ per niche. Zoho values = exactly the old text.
SCREEN_WORD = "Zoho screens" if IS_ZOHO else "Claude / tool screens"
SCREEN_PART = "Zoho-screen" if IS_ZOHO else "screen"
UPLOAD_TAGS = ["Zoho", "AI automation", "Shorts"] if IS_ZOHO else [str(t) for t in (CH.get("upload_tags") or ["Shorts"])]


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


def _beat(line):
    return str(line.get("beat", "")).upper()


def is_face(line):
    return _beat(line).startswith(FACE_BEATS)


def keep_lines(lines):
    """Script lines that go into the video (the follow / CTA line is dropped), each marked face or screen."""
    out = []
    for l in lines:
        if _beat(l).startswith(DROP_BEATS) or not _say(l):
            continue
        out.append(dict(l, face=is_face(l)))
    return out


# ------------------------------------------------------------------ script -> Flow clips
def chunks(lines):
    """Script -> Flow clips, ONLY for the face lines (HOOK / PROBLEM / RESULT). Consecutive face lines flow on,
    so each clip is filled up to MAX_WORDS (one 8 s clip); a clip ends at a sentence end (or comma) when it can.
    HOOK always gets its own clip. Returns [{"text", "lines": [line indexes], "beat"}] in script order."""
    groups, cur = [], []
    for i, l in enumerate(lines):
        words = _say(l).split()
        if not words:
            continue
        if not l.get("face", is_face(l)):
            if cur:
                groups.append(cur)
                cur = []
            continue
        solo = str(l.get("beat", "")).upper().startswith(("HOOK", "CTA"))
        if solo and cur:
            groups.append(cur)
            cur = []
        cur += [(w, i) for w in words]
        if solo:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    out = []
    for g in groups:
        k = 0
        while k < len(g):
            rest = len(g) - k
            if rest <= MAX_WORDS:
                cut = len(g)
            else:
                parts = -(-rest // MAX_WORDS)  # clips still needed for this group
                target = -(-rest // parts)  # even size
                lo, hi = k + max(4, int(target * 0.6)), min(k + MAX_WORDS, len(g) - 1)
                cut = k + target
                best = None
                for j in range(hi, lo - 1, -1):  # prefer a sentence end, then a comma
                    end = g[j - 1][0]
                    score = 2 if end[-1:] in ".!?" else 1 if end[-1:] in ",;:" else 0
                    if score and (best is None or score > best[0] or
                                  (score == best[0] and abs(j - k - target) < abs(best[1] - k - target))):
                        best = (score, j)
                if best:
                    cut = best[1]
            piece = g[k:cut]
            idx = sorted({i for _, i in piece})
            out.append({"text": " ".join(w for w, _ in piece), "lines": idx,
                        "beat": str(lines[piece[0][1]].get("beat", ""))})
            k = cut
    return out


_ACT = {"HOOK": "steps forward slightly with an energetic, curious expression and an open-hand gesture",
        "PROBLEM": "frowns a little and gestures with both hands, showing the frustration",
        "FIX": "nods confidently and counts on his fingers",
        "STEP": "points to the side as if showing something on a screen next to him",
        "RESULT": "smiles and opens both arms wide",
        "CTA": "smiles warmly and points at the camera"}


# 14 Oct 2026: gesture / body language har clip mein alag - channel.yaml flow.gestures (beat -> list) se,
# line ke text se seed hota hai (same line = same gesture, alag line = alag). Pool khaali ho to _ACT fallback.
_GEST = {str(k).upper(): [str(x).strip() for x in (v or []) if str(x).strip()]
         for k, v in (_F.get("gestures") or {}).items()}
BODY = (_F.get("body") or "").strip().rstrip(".")


def _act(beat, text):
    import random
    b = str(beat).upper()
    pool = next((v for k, v in _GEST.items() if k != "ANY" and b.startswith(k) and v), None) or _GEST.get("ANY")
    if pool:
        return random.Random(f"{b}|{text}").choice(pool)
    return next((v for k, v in _ACT.items() if b.startswith(k)), "explains with natural, lively hand gestures")


def prompt(text, beat="", look=None):
    look = SCENE if look is None else look
    act = _act(beat, text)
    cam = ("smooth gimbal camera gently moving back with him so the framing stays the same"
           if re.search(r"\bwalk", act) else "static camera")
    return (f"{PRESENTER} looks into the camera and talks to the viewer like a confident, friendly business tech "
            f"explainer, smart and natural, not stiff; he {act}. {SHOT}, {cam}, sharp and well lit"
            + (f", {look}" if look else "") + ". "
            + (f"{BODY}. " if BODY else "")
            + f"He says, in clear natural English with {ACCENT}, at a brisk, lively pace: \"{text}\" "
            "His lips match every word. He starts speaking in the very first frame, with no pause before the "
            "first word, and stops right after the last word. "
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


def _issue_closed(job):
    """A closed issue = this Short was already finished (or cancelled by hand). Never build / upload it again."""
    if not job.get("issue"):
        return False
    return _gh("GET", f"/issues/{job['issue']}").get("state") == "closed"


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
        *([f"**Today's look (same in every clip):** {job['look']}", ""] if job.get("look") else []),
        "### Steps (about 5 min)",
        "1. Open **https://flow.google.com** -> your project -> video settings **9:16**, model **Veo 3.1 - Fast**.",
        "2. Select **your avatar** (Characters), so every clip is you with your voice.",
        "3. For each box below: click the copy button (top-right of the box) -> paste in Flow -> generate -> "
        "**Download** the video.",
        f"4. Open **[this upload link]({upload_link(job['id'])})** -> drag **all** the clips in -> **Commit changes**.",
        "   Any file names, any order: the robot listens to every clip and matches it to its line.",
        f"5. Done. The robot cuts, joins, hides the Flow watermark, adds {SCREEN_WORD} + captions + music, checks the "
        "quality and schedules it on YouTube. This issue closes by itself.", "",
        "Retake a bad clip? Just upload the new one too - the clip that matches its line best is used.",
        "", "---", "", *rows])


def prepare(count, do_upload):
    """Daily run: research -> script -> clip prompts -> job folder + GitHub issue. Nothing is rendered.
    The scheduled run makes PER_DAY Shorts; a manual run may ask for more (up to flow.max_batch, e.g. a week)."""
    from . import notify, research, state, writer
    from .main import _lines, build_description, build_title
    count = max(1, min(count, max(PER_DAY, MAX_BATCH)))
    waiting = [p for p in JOBS.glob("*/job.json")] if JOBS.exists() else []
    waiting = [p for p in waiting
               if json.loads(p.read_text(encoding="utf-8")).get("status") == "waiting_for_clips"]
    if not IS_ZOHO:  # niche switch: only this niche's own waiting Shorts count (old Zoho ones never block it)
        waiting = [p for p in waiting
                   if (json.loads(p.read_text(encoding="utf-8")).get("niche") or "zoho") == NICHE_ID]
    if count <= PER_DAY and len(waiting) >= MAX_WAITING:
        print(f"[flow] {len(waiting)} Shorts already wait for clips - no new one today")
        return
    st = state.load()
    if IS_ZOHO:  # the Zoho niche, unchanged
        angles = writer.scout(research.fetch(st["covered_links"], covered_titles=st.get("covered_titles")),
                              count + EXTRA_ANGLES, st["problems"])
    else:  # niche switch: the rotation (4 wealth -> 1 problems) decides what kind of Short comes next
        from . import niche_claude_wealth as nw
        rot = st.setdefault("rotation", {}).get(NICHE_ID, 0)
        kinds = nw.needed_kinds(rot, count)
        inds = nw.needed_industries(st["rotation"].get(NICHE_ID + "_industry", 0), count)
        segs = nw.needed_segments(st["rotation"].get(NICHE_ID + "_segment", 0), count)
        topic = os.getenv("TOPIC", "").strip()  # Run workflow -> topic: this exact Short, today
        print(f"[flow] niche {NICHE_ID}: rotation position {rot} -> next Shorts: {kinds} / industries "
              f"{[i.get('id') for i in inds]} / segments {[x.get('id') for x in segs]}"
              + (f" / topic: {topic}" if topic else "") + (" / faceless" if FACELESS else " / with face clip"))
        angles = writer.scout(research.fetch(st["covered_links"]), count + 2, st["problems"], kinds,
                              industries=inds, topic=topic, segments=segs)
    print(f"[flow] scout found {len(angles)} angles")
    made, errors = 0, []
    for k, angle in enumerate(angles):
        if made >= count:
            break
        job_id = f"{dt.datetime.utcnow():%Y%m%d-%H%M}-{k + 1}"
        print(f"\n[flow] === [{angle.get('pillar', '')}] {angle.get('problem')}")
        try:
            sc = writer.approved_script(angle)
            if not IS_ZOHO and angle.get("industry"):  # niche v2: the composer colours the screens by industry
                sc["industry"] = angle["industry"]
            if not IS_ZOHO and angle.get("segment"):  # niche v4: segment (audience) colour + label win
                sc["segment"] = angle["segment"]
            lines = keep_lines(_lines(sc))
            clips = chunks(lines)
            if not clips and not FACELESS:
                raise RuntimeError("script has no spoken lines")
            if IS_ZOHO:
                look = pick_look(st) if clips else ""  # one look for every clip of this Short; a new one per Short
            else:  # niche v2: the place comes from the Short's industry, the outfit rotates
                look = nw.look_for(angle, st.get("look_index", 0)) or LOOKS[st.get("look_index", 0) % len(LOOKS)]
            st["look_index"] = st.get("look_index", 0) + 1
            for c in clips:
                c["prompt"] = prompt(c["text"], c["beat"], look)
            d = JOBS / job_id
            (d / "clips").mkdir(parents=True, exist_ok=True)
            (d / "clips" / ".keep").write_text("drop the Flow clips here\n")
            job = {"id": job_id, "niche": NICHE_ID, "status": "waiting_for_clips" if clips else "ready",
                   "upload": do_upload,
                   "created": dt.datetime.utcnow().isoformat(timespec="seconds"),
                   "title": build_title(sc), "description": build_description(sc, angle),
                   "angle": {k2: v for k2, v in angle.items() if k2 != "story"}, "story": angle.get("story"),
                   "script": sc, "lines": lines, "clips": clips, "look": look}
            body = _body(job)
            issue = _gh("POST", "/issues", {"title": f"🎬 Today's Short: {job['title'][:70]} "
                                                     + (f"({len(clips)} Flow clips)" if clips else "(no clip needed)"),
                                            "body": body, "assignees": [REPO.split("/")[0]]})
            job["issue"] = issue.get("number")
            (d / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "PROMPTS.md").write_text(body, encoding="utf-8")
            st["problems"].append(angle["problem"])
            if angle.get("story"):
                st["covered_links"].append(angle["story"]["link"])
                # 10 Nov 2026: the same story comes back from another publisher / link -> remember the title too
                st.setdefault("covered_titles", []).append(angle["story"].get("title", ""))
                st["covered_titles"] = st["covered_titles"][-200:]
            st["scripts"][f"S{st['next_id']:04d}"] = {"problem": angle["problem"], "title": job["title"],
                                                      "pillar": angle.get("pillar"), "engine": "flow",
                                                      "job": job_id, "created": job["created"]}
            st["next_id"] += 1
            if not IS_ZOHO:
                st.setdefault("rotation", {})[NICHE_ID] = st["rotation"].get(NICHE_ID, 0) + 1
                if not os.getenv("TOPIC", "").strip():  # a hand-picked topic does not use up an industry slot
                    for k in (NICHE_ID + "_industry", NICHE_ID + "_segment"):
                        st["rotation"][k] = st["rotation"].get(k, 0) + 1
            made += 1
            where = issue.get("html_url") or f"https://github.com/{REPO}/blob/main/jobs/{job_id}/PROMPTS.md"
            if clips: notify.send(f"🎬 {CHANNEL_NAME}: a new Short needs {len(clips)} Flow clips.\n"
                        f"Prompts: {where}\nUpload: {upload_link(job_id)}")
            print(f"[flow] job {job_id}: {len(clips)} clips -> {where}")
        except Exception as e:
            traceback.print_exc()
            errors.append(f"{angle.get('problem', '')[:60]}: {type(e).__name__}: {str(e)[:200]}")
        finally:
            state.save(st)
    if not made:
        raise RuntimeError("no Short prepared: " + "; ".join(errors[-3:]))


def fallback(min_age_h=20.0):
    """11 Nov 2026 (Gaurav: "Flow mein credit nahi bacha to faceless, warna mera face"): a Zoho Short whose Flow
    clips did not come within min_age_h hours is built FACELESS (Gaurav's photo cards + screens + one Gemini voice)
    and scheduled. Older than 4 days = stale news -> skipped. Returns how many jobs were switched."""
    switched = 0
    for jf in sorted(JOBS.glob("*/job.json")) if JOBS.exists() else []:
        job = json.loads(jf.read_text(encoding="utf-8"))
        if job.get("status") != "waiting_for_clips" or (job.get("niche") or "zoho") != NICHE_ID:
            continue
        if _clip_files(jf.parent):
            continue  # Gaurav / Claude already started uploading clips -> leave it
        try:
            made = dt.datetime.strptime(job["id"][:13], "%Y%m%d-%H%M").replace(tzinfo=dt.timezone.utc)
        except Exception:
            continue
        age = (dt.datetime.now(dt.timezone.utc) - made).total_seconds() / 3600
        if age > 96:
            job["status"] = "skip"
            print(f"[flow] {job['id']}: {age:.0f} h old, news is stale - skipped")
        elif NEVER_FACELESS:
            # 22 Nov 2026 (Gaurav): never faceless. No clips after EXPIRE_HOURS -> skip (not built), so the daily run
            # can write 2 fresh Shorts again (max_waiting would block it otherwise).
            if age < max(min_age_h, EXPIRE_HOURS):
                continue
            job["status"] = "skip_no_clips"
            print(f"[flow] {job['id']}: no Flow clips after {age:.0f} h -> skipped (Zoho Shorts are never faceless)")
            _comment(job, "⏭️ No Flow clips came for this Short in time, so it is skipped (Zoho Shorts are never "
                          "built faceless). Today's run writes fresh Shorts.")
        elif age >= min_age_h:
            for ln in job.get("lines", []):
                ln["face"] = False
            job.update(clips=[], faceless_fallback=True)
            switched += 1
            print(f"[flow] {job['id']}: no Flow clips after {age:.0f} h -> built FACELESS")
            _comment(job, "🙂 No Flow clips came for this Short, so it is built **faceless** now (your photo cards + "
                          "Zoho screens + the Gemini voice) and scheduled.")
        else:
            continue
        jf.write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    return switched


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


def speech_window(src, heard):
    """(start, end) of the actual speech in a clip. The loudness-based start wins over whisper's (whisper's VAD
    often starts early, which made every clip open with a slow, silent beat)."""
    from . import editor
    d = _dur(src)
    try:
        sp = editor.speech_spans(src, noise="-32dB", min_silence=0.15)
    except Exception:
        sp = []
    a = b = None
    if sp:
        a, b = sp[0][0], sp[-1][1]
    if heard:
        ha, hb = heard[0][0], heard[-1][1]
        a = ha if a is None else max(a, ha - 0.15)
        b = hb if b is None else min(max(b, hb), hb + 0.35)
    if a is None:
        a, b = 0.0, d
    a, b = max(0.0, a - LEAD), min(d, b + TAIL)
    if b - a < 0.6:
        a, b = 0.0, d
    return a, b


def prep_clip(src: Path, heard, out_v: Path, out_a: Path):
    """One clip: speech only (silence at both ends cut tight), pace x SPEED (voice and lips together), watermark
    hidden, 720x1280 @30, wav 44.1 kHz. Video and audio get exactly the same length, so lips never drift."""
    a, b = speech_window(src, heard)
    from .editor import black_spans
    for s0, s1 in black_spans(src, 0.04):  # Veo sometimes fades in from / out to black -> never use those frames
        if s0 <= a + 0.05 < s1:
            a = min(s1, b - 0.3)
        elif s0 < b - 0.05 <= s1:
            b = max(s0, a + 0.3)
    frames = max(int(round((b - a) / SPEED * FPS)), 1)
    length = frames / FPS
    chain, last = _hide_watermark("[0:v]", _size(src))
    fc = (f"{chain};{last}setpts=(PTS-STARTPTS)/{SPEED:.3f},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={FPS},setsar=1,format=yuv420p[v]")
    _run(_ff("-ss", f"{a:.3f}", "-i", str(src), "-filter_complex", fc, "-map", "[v]", "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-r", str(FPS), str(out_v)))
    _run(_ff("-ss", f"{a:.3f}", "-i", str(src), "-vn", "-ac", "1", "-ar", str(RATE), "-af",
             f"atempo={SPEED:.3f},apad=whole_dur={length:.3f}", "-t", f"{length:.3f}", "-c:a", "pcm_s16le",
             str(out_a)))
    return length


def join(parts, work: Path):
    """[(video, wav)] -> (avatar.mp4, voice.wav)"""
    vl, al = work / "v.txt", work / "a.txt"
    vl.write_text("".join(f"file '{v.resolve()}'\n" for v, _ in parts))
    normed = []
    for k, (_, a) in enumerate(parts):  # every part at the same loudness -> no volume jump between clip and screen voice
        n = work / f"n{k:02d}.wav"
        _run(_ff("-i", str(a), "-af", "loudnorm=I=-16:TP=-1.5:LRA=7,apad", "-ar", str(RATE), "-ac", "1",
                 "-t", f"{_dur(a):.4f}", "-c:a", "pcm_s16le", str(n)))
        normed.append(n)
    al.write_text("".join(f"file '{n.resolve()}'\n" for n in normed))
    av, raw, voice = work / "avatar.mp4", work / "voice_raw.wav", work / "voice.wav"
    _run(_ff("-f", "concat", "-safe", "0", "-i", str(vl), "-c", "copy", str(av)))
    _run(_ff("-f", "concat", "-safe", "0", "-i", str(al), "-c", "copy", str(raw)))
    _run(_ff("-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(RATE), "-ac", "1", str(voice)))
    return av, voice


_APP_WORDS = [("crm", "crm"), ("bigin", "crm"), ("campaigns", "crm"), ("books", "books"), ("invoice", "books"),
              ("desk", "desk"), ("creator", "creator"), ("inventory", "inventory"), ("analytics", "analytics"),
              ("salesiq", "salesiq"), ("zoho sign", "sign"), ("zoho social", "social"), ("zoho flow", "flow"),
              ("catalyst", "catalyst")]


def _fill_app(job, lines):
    """Older scripts have screen specs without "app" -> they were drawn as Zoho Books even for a CRM Short.
    Guess the app from the title (then description / spoken lines) and fill it in where it is missing."""
    texts = [job.get("title", ""), job.get("description", ""), " ".join(_say(l) for l in lines)]
    guess = None
    for t in texts:
        t = str(t).lower()
        hits = sorted((t.find(w), app) for w, app in _APP_WORDS if w in t)
        if hits:
            guess = hits[0][1]
            break
    if not guess or not IS_ZOHO:  # niche switch: the Zoho-app guess only applies to Zoho Shorts
        return
    for l in lines:
        sp = l.get("screen")
        if isinstance(sp, dict) and not str(sp.get("app") or "").strip() and \
                str(sp.get("view") or "").lower() in ("", "list", "form", "settings"):
            sp["app"] = guess


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
    covered = {li for c in clips for li in c["lines"]}
    lines = [dict(l, face=(i in covered)) for i, l in enumerate(job["lines"])]
    _fill_app(job, lines)
    parts, done_clips, timeline = [], set(), []
    # screen lines first, ALL in ONE voice: Gemini (= your avatar's voice); a backup voice only if Gemini is out
    screen = [(i, _say(l)) for i, l in enumerate(lines) if not l["face"]]
    voiced = {}
    if screen:
        from . import tts
        tdir = work / "tts"
        tdir.mkdir(parents=True, exist_ok=True)
        outs = [tdir / f"line{i:02d}.wav" for i, _ in screen]
        # 11 Nov 2026: with Flow avatar clips the screen voice must sound like Gaurav's avatar (Indian English). Gemini's
        # voices sound American (QA voice 30-40 on the Hotelogix Short) -> the Indian edge voice comes first there.
        # QA still checks strictly that it is the SAME-sounding man ("match"); faceless Shorts keep Gemini first.
        avatar = any(l.get("face") for l in lines)
        order = ("edge", "gemini", "piper") if avatar else ("gemini", "edge", "piper")
        job["_voice"] = tts.speak_all([t for _, t in screen], outs, RATE, order=order)
        voiced = {i: o for (i, _), o in zip(screen, outs)}
        if avatar:  # 11 Nov 2026 (Gaurav): "farq chalega" - a different screen voice is OK in avatar Shorts;
            pass    # QA gets the edge voice name -> voice difference is not a blocker, everything else stays strict
        elif job["_voice"] != "gemini":
            print(f"[flow] screen parts use the backup voice '{job['_voice']}' (Gemini TTS out of quota)")
    for i, l in enumerate(lines):
        if l["face"]:
            # a long line can be split over several clips (older jobs: HOOK / PROBLEM / RESULT in 2 clips each) -
            # use ALL of them in order, otherwise half the line's speech goes missing and captions/screens drift
            for ci in [k for k, c in enumerate(clips) if i in c["lines"] and k not in done_clips]:
                done_clips.add(ci)
                fi, _ = pick[ci]
                v, a = work / f"p{len(parts):02d}.mp4", work / f"p{len(parts):02d}.wav"
                timeline.append(("avatar", i, prep_clip(files[fi], heard[fi], v, a)))
                parts.append((v, a))
        else:  # Zoho-screen part: TTS voice + a placeholder video (the composer puts the screen exactly here)
            v, a = work / f"p{len(parts):02d}.mp4", work / f"p{len(parts):02d}.wav"
            timeline.append(("screen", i, tts_part(_say(l), v, a, voiced.get(i))))
            parts.append((v, a))
    av, voice = join(parts, work)
    # editor's ear: no dead air inside the Short
    sp = editor.speech_spans(voice, noise="-40dB", min_silence=1.2)
    for (_, e0), (s1, _) in zip(sp, sp[1:]):
        notes.append(f"dead air: {s1 - e0:.1f}s of silence at {e0:.1f}s")
    script_text = " ".join(_say(l) for l in lines)
    words = editor.align_to_script(editor.transcribe(voice, work), script_text, voice)
    mp4 = work / "short.mp4"
    composer.render(job["script"], lines, words, av, voice, work / "edit", mp4, timeline=timeline)
    if (work / "edit" / "cover.jpg").exists():  # thumbnail next to short.mp4 (artifacts / previews / YouTube)
        shutil.copy(work / "edit" / "cover.jpg", work / "cover.jpg")
    return mp4, notes


def tts_part(text, out_v: Path, out_a: Path, wav=None):
    """A screen line: TTS voice + a black 720x1280 placeholder video of exactly the same length."""
    from . import tts
    tmp = out_a.with_name(out_a.stem + "_t.wav")
    if wav is not None:  # already voiced by tts.speak_all (one voice for the whole Short)
        shutil.copy(wav, tmp)
    else:
        tts.speak(text, tmp, RATE)
    if TTS_SPEED > 1.0:  # niche v2: screen voice at the same pace as the clip (pitch stays the same)
        fast = tmp.with_name(tmp.stem + "_x.wav")
        _run(_ff("-i", str(tmp), "-af", f"atempo={TTS_SPEED:.3f}", "-ac", "1", "-ar", str(RATE),
                 "-c:a", "pcm_s16le", str(fast)))
        fast.replace(tmp)
    length = _dur(tmp) + 0.12
    frames = max(int(round(length * FPS)), 1)
    length = frames / FPS
    _run(_ff("-i", str(tmp), "-af", f"apad=whole_dur={length:.3f}", "-t", f"{length:.3f}", "-ac", "1",
             "-ar", str(RATE), "-c:a", "pcm_s16le", str(out_a)))
    _run(_ff("-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-frames:v", str(frames),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-r", str(FPS),
             str(out_v)))
    tmp.unlink(missing_ok=True)
    return length


def _still_pending(job_id):
    """True unless another (parallel) run already finished this Short: its job folder is gone from origin/main.
    Prevents the same Short being uploaded twice when two clip uploads trigger two assemble runs."""
    try:
        # v4: a faceless Short is written AND built in the same daily run - its folder is not committed yet, so it
        # cannot have been finished by another run
        if subprocess.run(["git", "ls-files", "--error-unmatch", f"jobs/{job_id}/job.json"], cwd=ROOT,
                          capture_output=True).returncode != 0:
            return True
        subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=ROOT, check=True, timeout=60)
        r = subprocess.run(["git", "cat-file", "-e", f"origin/main:jobs/{job_id}/job.json"], cwd=ROOT)
        return r.returncode == 0
    except Exception as e:
        print(f"[flow] could not check origin for {job_id}: {e}")
        return True


def finish():
    """Assembles every job whose clips are all uploaded. Returns the number of Shorts finished."""
    from . import benchmark, editor, google_apis as g, notify, schedule, state, writer
    jobs = sorted(JOBS.glob("*/job.json")) if JOBS.exists() else []
    done = 0
    for jf in jobs:
        d = jf.parent
        job = json.loads(jf.read_text(encoding="utf-8"))
        if str(job.get("status", "")).lower() in SKIP_STATUS:
            print(f"[flow] {job['id']}: status {job.get('status')} - skipped")
            continue
        if (job.get("niche") or "zoho") != NICHE_ID:  # niche switch: built by main.py with its own niche settings
            print(f"[flow] {job['id']}: niche '{job.get('niche') or 'zoho'}' (active: {NICHE_ID}) - built separately")
            continue
        files = _clip_files(d)
        need = len(job["clips"])
        if len(files) < need:
            print(f"[flow] {job['id']}: {len(files)}/{need} clips uploaded, waiting")
            continue
        if _issue_closed(job):
            print(f"[flow] {job['id']}: issue #{job['issue']} is closed (already finished) - marked done, skipped")
            job["status"] = "done"
            jf.write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
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
            report = benchmark.gate(mp4, sc, "flow", editor.check_media(mp4) + notes,
                                    voice=job.get("_voice", "gemini"))
            (work / "qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[qa] score={report['overall']}/{report['min_score']} approved={report['approved']}")
            (work / "short.json").write_text(json.dumps({k: job[k] for k in ("title", "description", "script")},
                                                        ensure_ascii=False, indent=1), encoding="utf-8")
            run_link = (f"https://github.com/{REPO}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
                        if os.getenv("GITHUB_RUN_ID") else "")
            # Gaurav watched this exact Short and said "upload it" -> job.json "owner_approved": true.
            # Only that one job skips the QA block; every other Short stays as strict as before.
            owner_ok = bool(job.get("owner_approved")) and not report["approved"]
            # v4 (Gaurav 1 Nov: "schedule everything, I unschedule what I don't like"): in a niche with
            # benchmark.publish_floor the QA SCORE no longer blocks - but a broken video still never goes out
            # (QA could not watch it, technical problems, black frames, or a score under the floor).
            floor = (CH.get("benchmark") or {}).get("publish_floor")
            if floor is not None and not report["approved"] and not report.get("fatal") \
                    and not report.get("tech_problems") and not report.get("black_frames") \
                    and float(report.get("overall") or 0) >= float(floor):
                print(f"[qa] {job['id']}: score {report['overall']} < {report['min_score']} but no technical problem "
                      f"and >= publish_floor {floor} - scheduling, Gaurav reviews it on YouTube")
                owner_ok = True
            if owner_ok:
                print(f"[qa] {job['id']}: QA said no ({report['overall']}/{report['min_score']}), "
                      f"but Gaurav approved it by hand (owner_approved) - uploading")
            if not report["approved"] and not owner_ok:
                issues = "\n".join(f"- {x}" for x in map(str, report["issues"][:6]))
                _comment(job, f"⚠️ QA failed ({report['overall']}/{report['min_score']}):\n{issues}\n\n"
                              f"Video to check: {run_link} (Artifacts). Upload retakes of the bad clips here: "
                              f"{upload_link(job['id'])}")
                job["status"] = "qa_failed"  # Control room: "QA failed - retake needed" (a retake upload rebuilds it)
                jf.write_text(json.dumps({k: v for k, v in job.items() if not k.startswith("_")},
                                         ensure_ascii=False, indent=1), encoding="utf-8")
                notify.send(f"⚠️ {CHANNEL_NAME}: Short {job['id']} failed QA ({report['overall']}/"
                            f"{report['min_score']}).\n{issues}\nRetakes: {upload_link(job['id'])}")
                continue
            if not _still_pending(job["id"]):
                print(f"[flow] {job['id']}: already finished by another run - not uploading again")
                continue
            st = state.load()
            msg = f"✅ Short ready. Video: {run_link} (Artifacts)."
            if job.get("upload", True):
                yt = g.youtube()
                old = job.get("replaces")  # 11 Nov 2026: a fixed rebuild replaces its earlier upload (made PRIVATE,
                if old and not job.get("replaced_done"):  # not deleted - reversible) and takes over its slot
                    try:
                        yt.videos().update(part="status", body={"id": old, "status": {
                            "privacyStatus": "private", "selfDeclaredMadeForKids": False}}).execute()
                        st["slots"] = [x for x in st["slots"] if x.get("video_id") != old]
                        job["replaced_done"] = True
                        print(f"[yt] old upload {old} set to PRIVATE (replaced by this rebuild)")
                    except Exception as e:
                        print(f"[yt] could not make {old} private: {str(e)[:200]}")
                try:  # what is really on the channel (manual uploads, other runs) also counts -> max 2 a day
                    yt_times = g.scheduled_times(yt)
                except Exception as e:
                    print(f"[schedule] could not read the channel's scheduled videos: {str(e)[:160]}")
                    yt_times = []
                when, slot = schedule.next_slot(st["slots"], youtube_times=yt_times)
                tags = list(sc.get("tags") or []) + UPLOAD_TAGS
                try:
                    loc = writer.localize(job["title"], job["description"], LOCALES)
                except Exception as e:
                    print(f"[localize] failed: {e}")
                    loc = {}
                vid = g.upload(yt, mp4, job["title"], job["description"], tags, schedule.to_rfc3339_utc(when),
                               localizations=loc)
                if (work / "cover.jpg").exists():  # 2 Nov 2026: the cover (title + Gaurav + Claude screen)
                    g.set_thumbnail(yt, vid, work / "cover.jpg")
                st["slots"].append(slot | {"video_id": vid, "title": job["title"]})
                for v in st["scripts"].values():
                    if v.get("job") == job["id"]:
                        v |= {"video_id": vid, "publish_at": when.isoformat()}
                msg = (f"✅ Scheduled for {when:%d %b %I:%M %p} IST: https://youtube.com/shorts/{vid}\n"
                       f"Video file: {run_link} (Artifacts).")
                print(f"[flow] scheduled for {when:%d %b %I:%M %p} IST: https://youtube.com/shorts/{vid}")
            state.save(st)
            if job.get("_voice") not in (None, "gemini", "match") and not any(l.get("face") for l in job.get("lines", [])):
                msg += (f"\n\nℹ️ The Gemini voice quota was used up, so the {SCREEN_PART} parts use the backup voice "
                        f"'{job['_voice']}' this time (your presenter clips keep your own voice).")
            _comment(job, msg)
            if job.get("issue"):
                _gh("PATCH", f"/issues/{job['issue']}", {"state": "closed"})
            shutil.rmtree(d)  # job done -> its folder (and clips) leave the repo
            done += 1
        except Exception as e:
            traceback.print_exc()
            _comment(job, f"⚠️ Could not build the Short: {type(e).__name__}: {str(e)[:300]}")
            notify.send(f"⚠️ {CHANNEL_NAME}: Short {job['id']} failed: {type(e).__name__}: {str(e)[:200]}")
        finally:
            shutil.rmtree(work / "edit", ignore_errors=True)
    print(f"[flow] {done} Short(s) finished")
    return done
