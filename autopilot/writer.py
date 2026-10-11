"""The AI team (free Gemini API). It writes and edits; YOU are the face and the voice.

1. Scout        - turns real questions/stories into PROBLEM -> FIX angles for Zoho users
2. Scriptwriter - writes a ~50-second solo script you read on camera (+ code for widget/Deluge/HTML fixes)
3. Reviewer     - checks facts, makes steps concrete, enforces the length, reviews the code
   QA agent     - independent pass/fail gate on every script and on every finished video (no human review)
4. Captions     - converts Devanagari Hinglish captions to Roman letters
5. Metadata     - title/description for videos you recorded without a script
6. Community    - replies to comments (skips anything risky)
"""
import json
import re
import time

from google import genai
from google.genai import types

from .config import (GEMINI_API_KEY, GEMINI_MODEL, CHANNEL_NAME, CHANNEL_HANDLE, LANGUAGE, NICHE, CTA,
                     SCRIPT_WORDS, EVERGREEN_FALLBACK)

_client = None
# Free-tier models get overloaded (503) at peak hours, so rotate through backups (unknown ones are skipped).
_BACKUPS = ("gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite")
_MODELS = [GEMINI_MODEL] + [m for m in _BACKUPS if m != GEMINI_MODEL]


_LANG_RULES = {
    "Hinglish": '"tts": Hindi words in DEVANAGARI and English/brand words in Latin script, e.g. '
                '"बस Zoho CRM में workflow rule बनाओ" (the voice engine pronounces this best).',
    "Hindi": '"tts": the line in Devanagari Hindi (brand names may stay in Latin script).',
    "English": '"tts": the same as "say".',
}


def _gemini():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise SystemExit("GEMINI_API_KEY missing")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def ask_json(prompt, temperature=0.7, retries=8):
    last = None
    for i in range(retries):
        model = _MODELS[i % len(_MODELS)]
        try:
            r = _gemini().models.generate_content(
                model=model, contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature, response_mime_type="application/json"))
            out = json.loads(r.text)
            if isinstance(out, list):
                out = {"items": out}
            return out
        except Exception as e:  # 503 overload / 429 rate limit / 404 unknown model -> next model
            last = e
            wait = 0 if "404" in str(e) else min(8 * (i + 1), 40)
            print(f"[gemini] {model} attempt {i + 1} failed: {str(e)[:160]}; retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Gemini failed: {last}")


def ask_text(prompt, temperature=0.6):
    for model in _MODELS:
        try:
            r = _gemini().models.generate_content(
                model=model, contents=prompt, config=types.GenerateContentConfig(temperature=temperature))
            return (r.text or "").strip()
        except Exception as e:
            print(f"[gemini] text {model} failed: {str(e)[:120]}")
            time.sleep(5)
    return ""


def word_count(text):
    return len(re.sub(r"\[[^\]]*\]", "", text or "").split())


def _examples():
    return "; ".join(f'"{p}"' for p in NICHE.get("good_problems", []))


def _solution_types():
    return "\n".join(f'  - "{k}": {v}' for k, v in NICHE.get("solution_types", {}).items())


# ---------------------------------------------------------------- 1. Scout
def scout(candidates, n, past_problems):
    listing = "\n".join(
        f"[{i}] {c['title']} | {c['source']} | {c['summary'][:400]}" for i, c in enumerate(candidates))
    past = "\n".join(f"- {p}" for p in past_problems[-60:]) or "- (none yet)"
    evergreen = ("If fewer than {n} items are good, ADD evergreen problems that Zoho users commonly face, "
                 "with story_index -1. Only use features you are sure exist in current Zoho products."
                 ).format(n=n) if EVERGREEN_FALLBACK else "Only use the items below."
    prompt = f"""You are the research lead of "{CHANNEL_NAME}", a {LANGUAGE} YouTube Shorts channel about
{NICHE['topic']} for {NICHE['audience']}. Each Short is presented by the channel's AI avatar presenter.
Our promise: {NICHE['promise']}

From the questions/stories below, find the {n} best "PROBLEM -> FIX" angles.
A good angle:
- is a painful, specific, everyday problem of a Zoho user, e.g. {_examples()}.
- has a fix that can be shown in 2-4 concrete steps (and, if needed, one short piece of code).
- uses one of these fix types:
{_solution_types()}
Skip {NICHE.get('skip', 'anything without a practical fix')}. Rules: {NICHE.get('safety', '')}.
{evergreen}
Do not repeat these recent problems:
{past}

Never invent Zoho features, menu names, prices or limits. If unsure about an exact menu path, describe it
generally ("Setup me Automation section").

Return JSON:
{{"angles": [{{
  "story_index": 0,
  "product": "Zoho CRM | Zoho Books | Zoho Creator | ...",
  "problem": "the pain in one {LANGUAGE} line, specific",
  "fix_type": "native | deluge | widget | html",
  "solution": "the fix in one line",
  "steps": ["step 1", "step 2", "step 3"],
  "result": "what the viewer gains",
  "hook": "a scroll-stopping first line in {LANGUAGE}, under 12 words, built on the problem"
}}]}}
Order from best to worst. Best = most Zoho users have this problem + clearest fix.

QUESTIONS / STORIES:
{listing or "(none today)"}"""
    angles = ask_json(prompt, temperature=0.5).get("angles", [])
    out = []
    for a in angles:
        i = a.get("story_index")
        if not a.get("problem"):
            continue
        if isinstance(i, int) and 0 <= i < len(candidates):
            a["story"] = candidates[i]
        elif EVERGREEN_FALLBACK:
            a["story"] = None
        else:
            continue
        out.append(a)
    return out[:n]


# ---------------------------------------------------------------- 2. Scriptwriter
def write_script(angle):
    lo, hi = SCRIPT_WORDS
    s = angle.get("story")
    source = (f"SOURCE (the question/story this came from): {s['title']} - {s['source']}\n{s['summary']}"
              if s else "SOURCE: evergreen problem, no news source. Do not mention any news.")
    prompt = f"""Write ONE YouTube Short script for "{CHANNEL_NAME}" in natural spoken {LANGUAGE}.
The video switches between the creator's lip-synced AI avatar and Zoho Books screens:
HOOK / PROBLEM / RESULT lines show the presenter talking to camera (keep them SHORT: they cost video credits);
FIX and every STEP line show the Zoho Books screen where that action happens, with the exact button / field highlighted while the voice says it.
So every STEP must be ONE concrete action in Zoho Books (where to go, what to click or fill), and its "screen"
must show exactly that (code goes in the description, not on screen).

THE ANGLE
Product: {angle.get('product')}
Problem: {angle.get('problem')}
Fix type: {angle.get('fix_type')}
Solution: {angle.get('solution')}
Steps: {json.dumps(angle.get('steps', []), ensure_ascii=False)}
Result: {angle.get('result')}
Hook idea: {angle.get('hook')}

{source}

STRUCTURE: HOOK (the problem as a punch, max 10 words) -> PROBLEM (ONE short line, max 14 words) -> FIX (1 line) ->
STEP 1..4 (each one clear action - the screen part is the heart of the video, give it the time) ->
RESULT (ONE short line, max 14 words, ends the video with a soft close like "set it up once and you are done").
NO CTA line: never ask to follow, like or subscribe.
No greeting, no intro, no "namaste doston".

RULES
- {lo}-{hi} words total in "say". Short sentences. "say" is Roman-script {LANGUAGE}.
- {_LANG_RULES.get(LANGUAGE, _LANG_RULES['English'])}
- "card": 2-7 word on-screen text for that line, e.g. "Setup > Automation > Workflow Rules".
- "screen" (FIX and every STEP line): a faithful mock of the real Zoho Books web screen for that action - real menu
  names only (Sales, Purchases, Items, Banking, Accountant, Reports, Settings > Preferences ...). Use "list" for
  record lists, "form" for create/edit pages, "settings" for preferences with toggles. 2-5 rows/fields.
- Never invent Zoho features, menus, prices or limits. If unsure of a menu name, say it generally.
- {NICHE.get('safety', '')}
- If the fix needs code (Deluge function, widget, HTML page), put WORKING, minimal, commented code in "code".
  Use placeholders like YOUR_ORG_ID / YOUR_API_DOMAIN, never real keys. Otherwise set "code" to null.

Return JSON:
{{
 "title": "YouTube title, max 70 chars, problem/fix led, honest",
 "hook_text": "max 6 words shown big at the top of the video",
 "lines": [{{"beat": "HOOK|PROBLEM|FIX|STEP 1|STEP 2|STEP 3|STEP 4|RESULT", "say": "Roman text",
            "tts": "text for the voice engine", "card": "on-screen text",
            "screen": null or (for FIX / STEP lines) {{"path": ["Sales", "Sales Orders"], "view": "list|form|settings",
                       "heading": "page title", "columns": ["..."], "rows": [["realistic Indian sample data"]],
                       "fields": [["Field label", "sample value"]], "toggles": [["Option label", true]],
                       "click": "EXACT text of the button / field / row cell / option to highlight (must appear on that screen)",
                       "tip": "max 8 words"}}}}],
 "code": {{"language": "deluge|html|javascript", "filename": "...", "content": "...",
          "where_to_paste": "exact place in Zoho"}} or null,
 "test_before_recording": ["what to check in your own Zoho account before recording"],
 "description": "2-3 lines: problem, fix, steps summary",
 "tags": ["10 short tags"]
}}"""
    return ask_json(prompt, temperature=0.8)


# ---------------------------------------------------------------- 3. Reviewer
def review_script(script, angle):
    lo, hi = SCRIPT_WORDS
    wc = word_count(" ".join(l.get("say", "") for l in script.get("lines", [])))
    prompt = f"""You are the strict editor of a solo {LANGUAGE} YouTube Short about {NICHE['topic']}.
Fix the JSON script below. Checklist:
1. FACTS: no invented Zoho features, menus, prices or limits. Soften anything you are not sure about.
2. STEPS: each step is a concrete action (what to open / click / paste). Rewrite vague steps.
3. LENGTH: total words in "say" must be {lo}-{hi} (now {wc}). Cut filler, keep hook and steps; remove any CTA / follow line.
4. HOOK: first line is a punchy problem statement under 12 words. No greeting.
5. CODE: if present, it must be minimal, correct and safe (no real keys, no deleting data). Fix bugs.
6. Roman-script {LANGUAGE} in "say"; every line keeps "beat", "say", "tts" and "card". {NICHE.get('safety', '')}
Return the corrected JSON only, same structure.

ANGLE: {json.dumps({k: v for k, v in angle.items() if k != 'story'}, ensure_ascii=False)}

SCRIPT:
{json.dumps(script, ensure_ascii=False)}"""
    try:
        fixed = ask_json(prompt, temperature=0.2)
    except Exception as e:
        print(f"[review] skipped: {e}")
        return script
    return fixed if fixed.get("lines") else script


# ---------------------------------------------------------------- 3b. QA agent (replaces human review)
def qa_script(script, angle):
    """A second, independent agent grades the script. Returns {"approved": bool, "issues": [...]}"""
    lo, hi = SCRIPT_WORDS
    prompt = f"""You are the quality gate of "{CHANNEL_NAME}", a {LANGUAGE} YouTube Shorts channel about
{NICHE['topic']}. Nobody else reviews this script before it is published, so be strict.

Reject (approved=false) if ANY of these is true:
- it states a Zoho feature, menu, price or limit that you are not confident exists today
- a step is vague (viewer would not know what to click / paste)
- the code (if any) has a bug, uses real keys, or could delete/overwrite data
- total words in "say" outside {lo}-{hi}, or the first line is not a punchy problem hook
- anything misleading, clickbait, or against: {NICHE.get('safety', '')}
- it mentions or implies affiliation with Zoho Corporation

Return JSON: {{"approved": true|false, "score": 1-10, "issues": ["specific problem + how to fix"]}}

ANGLE: {json.dumps({k: v for k, v in angle.items() if k != 'story'}, ensure_ascii=False)}
SCRIPT: {json.dumps(script, ensure_ascii=False)}"""
    out = ask_json(prompt, temperature=0.1)
    return {"approved": bool(out.get("approved")) and int(out.get("score") or 0) >= 7,
            "score": out.get("score"), "issues": out.get("issues") or []}


def fix_script(script, issues):
    prompt = f"""Fix this {LANGUAGE} YouTube Short script so that every issue below is solved. Keep the same JSON
structure and keys. Return JSON only.

ISSUES:
{json.dumps(issues, ensure_ascii=False)}

SCRIPT:
{json.dumps(script, ensure_ascii=False)}"""
    out = ask_json(prompt, temperature=0.3)
    return out if out.get("lines") else script


def approved_script(angle, rounds=3):
    """write -> edit -> QA gate, up to `rounds` fix loops. Raises if it never passes."""
    sc = review_script(write_script(angle), angle)
    issues = []
    for r in range(rounds):
        verdict = qa_script(sc, angle)
        print(f"[qa] script round {r + 1}: approved={verdict['approved']} score={verdict['score']}")
        if verdict["approved"]:
            return sc
        issues = verdict["issues"]
        sc = fix_script(sc, issues)
    raise RuntimeError("script failed the QA agent: " + "; ".join(map(str, issues))[:300])


def qa_video(mp4_path, meta):
    """Gemini watches the finished video. Returns {"approved": bool, "issues": [...]}"""
    client = _gemini()
    f = client.files.upload(file=str(mp4_path))
    for _ in range(30):                                  # wait until Google has processed the video
        f = client.files.get(name=f.name)
        if str(getattr(f.state, "name", f.state)) != "PROCESSING":
            break
        time.sleep(4)
    prompt = f"""You are the final quality check before this YouTube Short goes public on "{CHANNEL_NAME}".
Nobody else will watch it. Expected title: "{meta.get('title', '')}". The video has NO top banner / title card by design (only spoken-word captions), so never ask for one.
Reject only for real problems a viewer would notice:
- captions unreadable, cut off, overlapping, or clearly out of sync with the speech
- audio missing, distorted, or very quiet; long silences
- black / frozen / broken video, the face badly cropped, or a distorted / glitchy face or mouth
- content that does not match the title, or anything offensive or misleading
Return JSON: {{"approved": true|false, "issues": ["..."]}}"""
    try:
        for rnd in range(4):                             # 429 / 503 are usually temporary -> wait and go again
            for model in _MODELS:
                try:
                    r = client.models.generate_content(
                        model=model, contents=[f, prompt],
                        config=types.GenerateContentConfig(temperature=0.1, response_mime_type="application/json"))
                    out = json.loads(r.text)
                    return {"approved": bool(out.get("approved")), "issues": out.get("issues") or []}
                except Exception as e:
                    print(f"[qa] video check via {model} (round {rnd + 1}) failed: {str(e)[:160]}")
                    time.sleep(0 if "404" in str(e) else 5)
            time.sleep(30 * (rnd + 1))
    finally:
        try:
            client.files.delete(name=f.name)
        except Exception:
            pass
    raise RuntimeError("video QA agent unavailable")


# ---------------------------------------------------------------- 4. Captions
def romanize_words(words):
    """Devanagari/Hinglish words -> Roman Hinglish, same count. Returns None if it can't keep the count."""
    prompt = f"""Transliterate each item of this list of spoken Hinglish words into Roman script, the way
Indians type Hinglish on WhatsApp (e.g. "करना" -> "karna", "ज़ोहो" -> "Zoho", "सीआरएम" -> "CRM",
"वर्कफ़्लो" -> "workflow"). English/brand words get their normal English spelling. Keep punctuation.
Return JSON {{"words": [...]}} with EXACTLY {len(words)} items, same order, one output per input.

{json.dumps(words, ensure_ascii=False)}"""
    try:
        out = ask_json(prompt, temperature=0.0, retries=4).get("words")
    except Exception as e:
        print(f"[captions] romanize failed: {e}")
        return None
    if not isinstance(out, list) or len(out) != len(words):
        print(f"[captions] romanize returned {len(out) if isinstance(out, list) else 'bad'} items "
              f"for {len(words)} words; keeping original script")
        return None
    return [str(w) for w in out]


# ---------------------------------------------------------------- 5. Metadata for unscripted videos
def metadata_from_transcript(transcript):
    prompt = f"""This is the transcript of a {LANGUAGE} YouTube Short recorded by the creator of
"{CHANNEL_NAME}" ({NICHE['topic']}). Write honest metadata based ONLY on what is said.

TRANSCRIPT:
{transcript[:4000]}

Return JSON: {{"title": "max 70 chars, problem/fix led", "hook_text": "max 6 words for the top of the video",
"description": "2-3 lines", "tags": ["10 short tags"]}}"""
    return ask_json(prompt, temperature=0.4)


# ---------------------------------------------------------------- 6. Community
def suggest_reply(comment, video_title):
    prompt = f"""You draft replies to YouTube comments for {CHANNEL_NAME} ({CHANNEL_HANDLE}), a {LANGUAGE}
Shorts channel: {NICHE['promise']}
Your reply is posted automatically, so when in doubt answer SKIP.
Video: "{video_title}"
Comment: "{comment}"

If the comment is spam, abusive, flame-bait, asks for personal/financial/legal/tax advice, or needs a
fact you are not sure about, answer exactly SKIP.
If they describe a Zoho problem, thank them and say it may become a Short.
Otherwise write ONE short, friendly reply (max 30 words) in the same language style as the comment.
No links, no promises, no made-up facts."""
    out = ask_text(prompt)
    return None if (not out or out.strip().upper().startswith("SKIP")) else out[:400]
