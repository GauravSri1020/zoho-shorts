"""Benchmark agent + upload gate ("would this Short survive next to the best Zoho Shorts on YouTube?").

1. learn():  every 14 days Gemini WATCHES the reference Shorts (channel.yaml -> benchmark.references, plus the
             most-viewed Zoho Books Shorts found on YouTube) and writes a scoring rubric -> state/benchmark.json
2. gate():   Gemini watches OUR finished Short next to that rubric and scores it 0-100 per criterion.
             Upload is allowed ONLY if
               - the avatar really lip-syncs (engine == sadtalker),
               - the technical checks passed,
               - overall score >= benchmark.min_score (default 75) and no criterion is a "blocker".
             If Gemini can't watch it (quota / outage) the answer is NO - never upload unchecked.
The full report is saved next to the video as qa.json (also inside the GitHub artifact).
"""
import datetime as dt
import json
import re
import time

from .config import CH, CHANNEL_NAME, STATE_DIR

_B = CH.get("benchmark", {}) or {}
MIN_SCORE = int(_B.get("min_score", 75))
REFS = _B.get("references", []) or []
SEARCH = _B.get("youtube_search", "Zoho Books")
FILE = STATE_DIR / "benchmark.json"
MAX_AGE_DAYS = 14

CRITERIA = {
    "hook": "first 2 seconds: is the problem clear and does it stop the scroll? (big title + spoken hook)",
    "avatar": "presenter looks like a real person talking: lips match the words, natural face, not a frozen photo",
    "zoho_screens": "the Zoho Books steps are SHOWN on screen, the exact button/field is highlighted, readable",
    "pacing": "visual change every 2-4 s, no dead time, length fits the content (25-60 s)",
    "captions": "readable, in sync, match the speech exactly, not covering important parts",
    "audio": "clear voice, natural Hinglish, music present but quiet under the voice",
    "value": "a Zoho Books user learns a real, correct fix they can follow",
    "polish": "looks as professional as the reference Shorts (layout, fonts, colours, no glitches)",
}


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
        prompt = f"""Watch this YouTube Short. Our channel "{CHANNEL_NAME}" makes Hinglish Zoho Books problem->fix Shorts
with an AI avatar of the creator + Zoho Books screens. Owner's note about this reference: "{ref.get('note', '')}".
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


def gate(mp4, sc, engine, tech_problems):
    """Returns the QA report dict; report["approved"] decides the upload."""
    report = {"engine": engine, "min_score": MIN_SCORE, "tech_problems": list(tech_problems or []),
              "scores": {}, "overall": 0, "issues": [], "approved": False, "fatal": False}
    if engine != "sadtalker":
        report["issues"].append("Avatar is not lip-synced (SadTalker did not run) - a still photo is not allowed.")
        report["fatal"] = True
    if tech_problems:
        report["issues"] += [f"technical: {p}" for p in tech_problems]
    bm = load()
    refs = [{k: r.get(k) for k in ("url", "note", "hook", "layout", "visuals", "cuts_per_10s", "captions",
                                    "presenter", "music", "what_to_copy")} for r in bm.get("references", [])]
    from google.genai import types
    prompt = f"""You are the strict final reviewer for the YouTube channel "{CHANNEL_NAME}" (Hinglish Zoho Books tips).
The attached video is OUR new Short. It must be as good as the best Shorts in the niche, otherwise it is NOT uploaded.
Expected title: "{sc.get('title', '')}". Expected top title text: "{sc.get('hook_text', '')}".
Script (what should be said and shown): {json.dumps([{k: l.get(k) for k in ('beat', 'say', 'card')} for l in sc.get('lines', [])], ensure_ascii=False)}

What the reference Shorts do (learned by watching them): {json.dumps(refs, ensure_ascii=False)[:9000]}

Score each criterion 0-100 compared with those references (70 = as good as an average reference, 90 = as good as the best):
{json.dumps(CRITERIA, ensure_ascii=False, indent=1)}
Mark a criterion as blocker if a viewer would clearly find it bad/fake/broken (e.g. lips not moving, wrong Zoho steps,
unreadable screens, captions not matching speech, silence, glitches).
Return JSON: {{"scores": {{"hook": 0, ...}}, "blockers": ["criterion names"], "overall": 0,
 "issues": ["specific problems with timestamps"], "fixes": ["what to change next time"],
 "vs_references": "one honest sentence"}}"""
    try:
        f = _upload_video(mp4)
        d = _ask([types.Content(role="user", parts=[types.Part(file_data=types.FileData(file_uri=f.uri,
                                                                                        mime_type="video/mp4")),
                                                      types.Part(text=prompt)])])
        report["scores"] = d.get("scores", {})
        report["blockers"] = d.get("blockers", [])
        vals = [float(v) for v in report["scores"].values() if isinstance(v, (int, float))]
        report["overall"] = round(min(float(d.get("overall", 0) or 0), sum(vals) / len(vals) if vals else 0), 1)
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
