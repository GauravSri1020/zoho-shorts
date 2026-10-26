"""Benchmark agent + upload gate ("would this Short survive next to the best Zoho Shorts on YouTube?").

1. learn():  every 14 days Gemini WATCHES the reference Shorts (channel.yaml -> benchmark.references, plus the
             most-viewed Zoho Books Shorts found on YouTube) and writes a scoring rubric -> state/benchmark.json
2. gate():   Gemini watches OUR finished Short next to that rubric and scores it 0-100 per criterion.
             Upload is allowed ONLY if
               - the avatar really lip-syncs (engine == flow: Google Flow clips with their own voice),
               - the technical checks passed,
               - overall score >= benchmark.min_score (default 75) and no criterion is a "blocker".
             If Gemini can't watch it (quota / outage) the answer is NO - never upload unchecked.
The full report is saved next to the video as qa.json (also inside the GitHub artifact).
"""
import datetime as dt
import json
import re
import time

from .config import CH, CHANNEL_NAME, STATE_DIR, IS_ZOHO

_B = CH.get("benchmark", {}) or {}
MIN_SCORE = int(_B.get("min_score", 75))
MIN_CRITERION = int(_B.get("min_criterion", 50))  # any single criterion below this blocks the upload
REFS = _B.get("references", []) or []
SEARCH = _B.get("youtube_search", "Zoho Books")
FILE = STATE_DIR / ("benchmark.json" if IS_ZOHO else "benchmark_claude_wealth.json")  # niche switch: own rubric
MAX_AGE_DAYS = 14

CRITERIA = {
    "hook": "first 2 seconds: is the problem clear and does it stop the scroll? (big title + spoken hook)",
    "avatar": "presenter looks like a real person talking: lips match every word, natural face and hands (no morphing, "
              "extra fingers, frozen photo), gestures fit the words",
    "continuity": "clean editing: no black / blank / frozen frame anywhere, no glitch or broken cut, the presenter has "
                  "the SAME outfit and background in every shot, no Flow watermark, nothing cut off at the edges",
    "voice": "one consistent, natural voice (same timbre, accent, pace and loudness in presenter and screen parts), "
             "no cut-off words, clicks, robotic words or dead air",
    "zoho_screens": "the Zoho / AI / API steps are SHOWN on screen at the moment they are said, the exact button / "
                    "field is highlighted, readable on a phone",
    "pacing": "visual change every 2-4 s, no dead time, length fits the content (25-60 s)",
    "captions": "readable, in sync, match the speech exactly, never covering the face or the important part of the screen",
    "audio": "clear voice, music present but always quieter than the voice",
    "value": "the viewer learns a real, correct fix they can follow",
    "polish": "looks as professional as the reference Shorts (layout, fonts, colours, no glitches)",
}

# NICHE SWITCH (27 Oct 2026): the words that describe the niche. Zoho values = exactly the old text; the checks,
# scores, blockers and limits are the SAME for every niche (quality stays as strict as before).
_QA_NICHE = "English AI + Zoho automation Shorts"
_QA_LEARN = "English Zoho problem->fix Shorts\nwith an AI avatar of the creator + Zoho Books screens"
_QA_PART = "Zoho-screen"
_QA_SCREENS = ("the Zoho / AI / API screen shows what is being said at that moment, readable on a phone, the highlight is\n"
               "   on the right button / field, it looks like the real app")
_QA_STORY = "hook in the first 2 s, the fix is correct and complete, the video ends cleanly (no abrupt cut)"
if not IS_ZOHO:
    from . import niche_claude_wealth as _nw
    CRITERIA = {("screens" if k == "zoho_screens" else k): v for k, v in CRITERIA.items()}
    CRITERIA["screens"] = _nw.QA_SCREENS
    CRITERIA["value"] = _nw.QA_VALUE
    _QA_NICHE, _QA_LEARN, _QA_PART, _QA_SCREENS, _QA_STORY = (_nw.QA_NICHE, _nw.QA_LEARN, _nw.QA_SCREEN_PART,
                                                              _nw.QA_SCREENS, _nw.QA_STORY)


def _yt_id(url):
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def _client():
    from . import writer
    return writer._gemini(), writer._MODELS


def _ask(contents, retries=6):
    """Gemini JSON call that rotates models; raises if every model fails."""
    from google.genai import types
    client, models = _client()
    last = None
    for i in range(retries):
        model = models[i % len(models)]
        try:
            r = client.models.generate_content(
                model=model, contents=contents,
                config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json"))
            return json.loads(r.text)
        except Exception as e:
            last = e
            print(f"[benchmark] {model} attempt {i + 1} failed: {str(e)[:140]}")
            time.sleep(min(60, 8 * (i + 1)))
    raise RuntimeError(f"Gemini unavailable: {str(last)[:200]}")


def _search_top(yt, n=4):
    """Most-viewed recent Shorts in the niche (needs the YouTube API; skipped when not available)."""
    if not yt:
        return []
    try:
        since = (dt.datetime.utcnow() - dt.timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = yt.search().list(part="snippet", q=f"{SEARCH} #shorts", type="video", videoDuration="short",
                             order="viewCount", publishedAfter=since, maxResults=n, relevanceLanguage="hi").execute()
        return [{"url": f"https://www.youtube.com/shorts/{it['id']['videoId']}", "note": it["snippet"]["title"],
                 "weight": 1} for it in r.get("items", [])]
    except Exception as e:
        print(f"[benchmark] YouTube search skipped: {str(e)[:150]}")
        return []


def load():
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def learn(yt=None, force=False):
    """Watches the reference Shorts and stores what makes them work. Cheap to call: refreshes every 14 days."""
    old = load()
    if old.get("updated") and not force:
        age = dt.datetime.utcnow() - dt.datetime.fromisoformat(old["updated"])
        if age.days < MAX_AGE_DAYS:
            return old
    from google.genai import types
    refs = list(REFS) + [r for r in _search_top(yt) if _yt_id(r["url"]) not in {_yt_id(x["url"]) for x in REFS}]
    notes = []
    for ref in refs[:10]:
        vid = _yt_id(ref.get("url"))
        if not vid:
            continue
        prompt = f"""Watch this YouTube Short. Our channel "{CHANNEL_NAME}" makes {_QA_LEARN}. Owner's note about this reference: "{ref.get('note', '')}".
Describe precisely what makes it work. Return JSON:
{{"length_s": 0, "hook": "what happens in the first 2 s", "layout": "screen layout (title bar, panels, split screen...)",
 "visuals": ["kinds of shots used"], "cuts_per_10s": 0, "captions": "style/position/colours",
 "presenter": "who is on screen and how they look/talk", "music": "type/volume or none",
 "on_screen_text": "titles, labels", "what_to_copy": ["5 concrete things our videos should copy"],
 "avoid": ["things not to copy"]}}"""
        try:
            d = _ask([types.Content(role="user", parts=[
                types.Part(file_data=types.FileData(file_uri=f"https://www.youtube.com/watch?v={vid}")),
                types.Part(text=prompt)])], retries=3)
            d |= {"url": ref["url"], "weight": ref.get("weight", 1), "note": ref.get("note", "")}
            notes.append(d)
            print(f"[benchmark] learned from {ref['url']}")
        except Exception as e:
            print(f"[benchmark] could not watch {ref.get('url')}: {str(e)[:150]}")
    if not notes:
        print("[benchmark] no reference could be analysed; keeping the old rubric")
        return old
    data = {"updated": dt.datetime.utcnow().isoformat(timespec="seconds"), "references": notes,
            "criteria": CRITERIA}
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def _upload_video(path):
    client, _ = _client()
    f = client.files.upload(file=str(path))
    for _ in range(40):
        f = client.files.get(name=f.name)
        if str(getattr(f.state, "name", f.state)) != "PROCESSING":
            break
        time.sleep(4)
    return f


def gate(mp4, sc, engine, tech_problems, voice="gemini"):
    """Returns the QA report dict; report["approved"] decides the upload.
    voice = who voiced the Zoho-screen parts: "gemini" = the avatar's own voice, so ANY voice change is a blocker;
    anything else = backup voice because the Gemini quota was used up -> a voice change there is expected."""
    report = {"engine": engine, "min_score": MIN_SCORE, "min_criterion": MIN_CRITERION, "voice": voice,
              "tech_problems": list(tech_problems or []), "scores": {}, "overall": 0, "issues": [],
              "approved": False, "fatal": False}
    if engine not in ("flow", "kaggle", "veo", "sadtalker"):
        report["issues"].append("Avatar is not lip-synced (Veo / SadTalker did not run) - a still photo is not allowed.")
        report["fatal"] = True
    if tech_problems:
        report["issues"] += [f"technical: {p}" for p in tech_problems]
    bm = load()
    refs = [{k: r.get(k) for k in ("url", "note", "hook", "layout", "visuals", "cuts_per_10s", "captions",
                                   "presenter", "music", "what_to_copy")} for r in bm.get("references", [])]
    from google.genai import types
    voice_rule = (f"ONE voice from start to end: the presenter clips and the {_QA_PART} parts must sound like the SAME "
                  "man (timbre, accent, pace, loudness). A different voice anywhere is a blocker." if voice == "gemini"
                  else f"Today the {_QA_PART} parts use a backup voice ('{voice}') because the AI-voice quota was used "
                  "up - a different voice on the screen parts is expected and NOT a blocker, but every part must be "
                  "clear, natural and at the same loudness.")
    prompt = f"""You are the senior video editor AND the strict final QA for the YouTube channel "{CHANNEL_NAME}"
({_QA_NICHE}). Watch the attached Short second by second - picture AND sound - exactly like a
professional editor does before publishing. It is uploaded ONLY if it is as good as the best Shorts in the niche;
when in doubt, it fails. Being strict here protects the channel.
Expected title: "{sc.get('title', '')}". Expected top title text: "{sc.get('hook_text', '')}".
Script (what should be said and shown): {json.dumps([{k: l.get(k) for k in ('beat', 'say', 'card')} for l in sc.get('lines', [])], ensure_ascii=False)}

What the reference Shorts do (learned by watching them): {json.dumps(refs, ensure_ascii=False)[:9000]}

Editor's checklist - check EVERY point and give a timestamp (m:ss) for each defect:
1. Picture: any black, blank or frozen frame (even 0.1 s), flash, glitch, broken cut, Flow watermark, head / hands cut off.
2. Presenter: lips match every word, natural face and hands (no morphing, extra fingers), gestures fit the words,
   the SAME outfit and background in every presenter shot.
3. Voice: {voice_rule} Also: no sudden loudness jump, click / pop, cut-off word, robotic word, silence over 0.8 s.
4. Screens: {_QA_SCREENS}.
5. Captions: exactly the spoken words, in sync, never covering the face or the important part of the screen.
6. Music: present but always quieter than the voice.
7. Story: {_QA_STORY}.

Score each criterion 0-100 compared with those references (70 = as good as an average reference, 90 = as good as the best):
{json.dumps(CRITERIA, ensure_ascii=False, indent=1)}
Mark a criterion as blocker if a viewer would clearly find it bad / fake / broken.
Return JSON: {{"scores": {{"hook": 0, ...}}, "blockers": ["criterion names"], "overall": 0,
 "black_frames": ["m:ss-m:ss of every black / blank moment; empty list if none"],
 "voice_changes": ["m:ss what changes; empty list if the voice stays the same"],
 "issues": ["specific problems with timestamps"], "fixes": ["what to change next time"],
 "vs_references": "one honest sentence"}}"""
    try:
        f = _upload_video(mp4)
        d = _ask([types.Content(role="user", parts=[types.Part(file_data=types.FileData(file_uri=f.uri,
                                                                                        mime_type="video/mp4")),
                                                      types.Part(text=prompt)])])
        report["scores"] = d.get("scores", {})
        vals = [float(v) for v in report["scores"].values() if isinstance(v, (int, float))]
        report["overall"] = round(min(float(d.get("overall", 0) or 0), sum(vals) / len(vals) if vals else 0), 1)
        report["black_frames"] = [str(x) for x in (d.get("black_frames") or []) if str(x).strip()]
        report["voice_changes"] = [str(x) for x in (d.get("voice_changes") or []) if str(x).strip()]
        blockers = [str(b) for b in (d.get("blockers") or [])]
        if report["black_frames"]:
            blockers.append("continuity")
            report["issues"] += [f"black / blank picture at {x}" for x in report["black_frames"]]
        if report["voice_changes"] and voice == "gemini":
            blockers.append("voice")
            report["issues"] += [f"voice changes at {x}" for x in report["voice_changes"]]
        low = [k for k, v in report["scores"].items() if isinstance(v, (int, float)) and v < MIN_CRITERION]
        if low:
            blockers += low
            report["issues"].append(f"below the minimum of {MIN_CRITERION}: "
                                    + ", ".join(f"{k} {report['scores'][k]}" for k in low))
        report["blockers"] = list(dict.fromkeys(blockers))
        report["issues"] += d.get("issues", [])
        report["fixes"] = d.get("fixes", [])
        report["vs_references"] = d.get("vs_references", "")
    except Exception as e:
        report["issues"].append(f"QA agent could not watch the video ({str(e)[:160]}) - not uploading unchecked.")
        report["fatal"] = True
        return report
    report["approved"] = (not report["fatal"] and not tech_problems and not report.get("blockers")
                          and report["overall"] >= MIN_SCORE)
    return report
