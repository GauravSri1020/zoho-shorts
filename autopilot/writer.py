"""The AI team (free Gemini API). It writes and edits; YOU are the face and the voice.

1. Scout - turns trending news, real questions and the problem bank into PROBLEM -> AI/ZOHO FIX angles
2. Scriptwriter - writes a ~50-second solo script (+ code / API call / AI prompt for the fix)
3. Reviewer - checks facts, makes steps concrete, enforces the length, reviews the code
   QA agent - independent pass/fail gate on every script and on every finished video (no human review)
4. Captions - converts Devanagari Hinglish captions to Roman letters
5. Metadata - title/description for videos you recorded without a script
6. Community - replies to comments (skips anything risky)
7. Localizer - title + description in Arabic, German, French, Spanish, Hindi (channel.yaml -> localize)
"""
import json
import re
import time

from google import genai
from google.genai import types

from .config import (GEMINI_API_KEY, GEMINI_MODEL, CHANNEL_NAME, CHANNEL_HANDLE, LANGUAGE, NICHE, CTA,
                     SCRIPT_WORDS, EVERGREEN_FALLBACK, PILLARS, IS_ZOHO, TRENDING_ONLY)

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

# What the screen part of a Short can show (autopilot/screens.py draws each of these).
APPS = ("crm", "books", "desk", "creator", "social", "flow", "analytics", "sign", "catalyst", "salesiq",
        "inventory", "people", "campaigns", "claude", "chatgpt", "api", "code")
VIEWS = ("list", "form", "settings", "chat", "api", "code", "flow")
if not IS_ZOHO:  # niche switch: the Claude-wealth screens (+ the "notes" numbers / checklist card)
    from .niche_claude_wealth import APPS  # noqa: E402,F811
    VIEWS = ("chat", "api", "code", "flow", "notes")


def _niche():
    """NICHE SWITCH (27 Oct 2026): the non-Zoho niche's prompts live in their own module; Zoho never loads it."""
    from . import niche_claude_wealth
    return niche_claude_wealth


def _gemini():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise SystemExit("GEMINI_API_KEY missing")
        _client = genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=120000))  # 2 min max per call (11 Nov: 504s at 5 min each made one script round take 6 min)
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


def news_facts(story):
    """10 Nov 2026: a headline alone made the writer invent menus ("Settings > AI Agents > Link Data Source").
    Before writing, Gemini + Google Search collects the REAL facts of the news (what launched, exact feature names,
    where it is in the product IF official docs say so, plans / availability, dates). Added to the story summary, so
    the writer AND the QA agent check against them. Empty string if search is not available today."""
    from google.genai import types as _t
    prompt = (f"Search the web for this Zoho news and list ONLY verified facts, with the source site after each fact:\n"
              f"NEWS: {story.get('title')} ({story.get('source')})\n\n"
              "1. What exactly Zoho launched / changed and when. 2. The exact names of new features. "
              "3. Where a user finds or switches it on in the product - ONLY if an official Zoho page or help doc says "
              "it (exact menu path); otherwise write 'menu path: not published'. 4. Plans / pricing / availability / "
              "regions / preview status. 5. Anything a business can do with it today. "
              "Max 15 short bullet lines. No guesses, no marketing words.")
    for model in _MODELS:
        try:
            r = _gemini().models.generate_content(
                model=model, contents=prompt,
                config=_t.GenerateContentConfig(temperature=0.1, tools=[_t.Tool(google_search=_t.GoogleSearch())]))
            text = (r.text or "").strip()
            if len(text) > 120:
                print(f"[facts] {len(text)} chars from Google Search ({model})")
                return text[:2500]
        except Exception as e:
            print(f"[facts] {model} failed: {str(e)[:140]}")
    return ""


def word_count(text):
    return len(re.sub(r"\[[^\]]*\]", "", text or "").split())


def _examples():
    return "; ".join(f'"{p}"' for p in NICHE.get("good_problems", []))


def _solution_types():
    return "\n".join(f'   - "{k}": {v}' for k, v in NICHE.get("solution_types", {}).items())


def _pillars():
    if not PILLARS:
        return "   - problem_fix: a real Zoho problem and its fix"
    return "\n".join(f'   - "{k}" (weight {v.get("weight", 1)}): {v.get("about", "")}' for k, v in PILLARS.items())


# ---------------------------------------------------------------- 1. Scout
def _trending_rules(candidates, n):
    """10 Nov 2026 (Gaurav): ONLY trending news. These rules go on top of the scout prompt and win over it."""
    news = [f"[{i}] {c.get('age_hours', '?')}h old, score {c.get('score', 0)}, {c.get('publishers', 1)} publishers: "
            f"{c['title']} | {c['source']}" for i, c in enumerate(candidates) if c.get("type") == "news"]
    return f"""HARD RULE FOR TODAY (it overrides everything below): this channel ONLY makes Shorts about TRENDING ZOHO NEWS.
- Every angle MUST be built on ONE of the ZOHO NEWS items listed here (its story_index), published in the last days.
  Prefer the highest score (= many publishers carry it + it is very fresh).
- Best Zoho news: a Zoho launch / update / new feature (Zia, Zia agents, Zoho MCP, Zoho CRM, Books, Desk, Flow,
  Creator, Analytics, Zoho One ...), a new integration or partnership, a plan / pricing / limit change, a compliance
  change Zoho now supports (e-invoicing, GST, ZATCA ...), or Zoho itself trending (a Zoho app going viral, a big
  adoption story).
- ALSO GOOD (11 Nov 2026): a new integration / partnership ("Hotelogix now connects to Zoho Books" -> what it means
  for hotels and how the connected flow works), and a customer story with a concrete result ("Optiven cut software
  costs 40% with Zoho" -> how a business does the same consolidation in Zoho), a telco / reseller launching Zoho
  for its business customers (-> what those businesses get and the first automation to set up).
- Skip only stories with nothing a Zoho user can DO or learn (court cases, investors, funding, personal opinions,
  "alternatives to Zoho" lists, job / HR gossip).
- The angle = "Zoho just did / announced THIS -> what it means for your business -> how to use / set it up in Zoho
  today". The hook MUST name the news (e.g. "Zoho just launched X - here's how to switch it on in 20 seconds").
- Use only facts that are in the news item. Never invent dates, numbers, features, menus or prices; if the news
  does not say where a setting is, describe it generally.
- Community questions (reddit / stackoverflow) may only support the problem; they can NEVER be the story_index.
- NO evergreen / problem-bank / generic Zoho tips. story_index -1 is NOT allowed. Return {n} angles when {n} news
  items qualify; fewer only when fewer qualify - but if ANY news item above is a launch, integration, partnership or
  customer story, at least one angle is expected.
- Set "pillar" to "trending".
NEWS ITEMS (best first):
{chr(10).join(news) or "(no fresh Zoho news today)"}"""


def scout(candidates, n, past_problems, kinds=None, industries=None, topic="", segments=None):
    if not IS_ZOHO:  # niche switch - everything below is the Zoho niche, unchanged
        return _niche().scout(candidates, n, past_problems, kinds, industries=industries, topic=topic,
                              segments=segments)
    listing = "\n".join(
        f"[{i}] (trend {c.get('trend', 0)}) {c['title']} | {c['source']} | {c['summary'][:400]}"
        for i, c in enumerate(candidates))
    past = "\n".join(f"- {p}" for p in past_problems[-60:]) or "- (none yet)"
    evergreen = ("If fewer than {n} items are good, ADD strong problems you know Zoho users face, "
                 "with story_index -1. Only use features you are sure exist in current Zoho products."
                 ).format(n=n) if EVERGREEN_FALLBACK else "Only use the items below."
    prompt = f"""You are the research lead of "{CHANNEL_NAME}", a {LANGUAGE} YouTube Shorts channel about
{NICHE['topic']}, for {NICHE['audience']}. Each Short is presented by the channel's AI avatar presenter.
Our promise: {NICHE['promise']}

Goal: Shorts that TREND this month and solve a real business problem. Prefer, in this order:
1. A topic that is trending right now (high "trend" number, or this week's AI launch / deadline) turned into
   "here is how you use it inside Zoho today".
2. A fix where AI does the work (Claude / ChatGPT over Zoho MCP, Zia agents, an AI step in Zoho Flow, Deluge
   calling an AI API) - future-proof, rare, and impressive enough that a Zoho expert would be surprised.
3. High-value business topics advertisers pay for: sales pipeline, lead generation and conversion, invoicing
   and getting paid, customer support, compliance deadlines, developer APIs.

Content pillars (mix them; the weight is how often):
{_pillars()}

From the items below, find the {n} best "PROBLEM -> FIX" angles.
A good angle:
- is a painful, specific, everyday problem of a business that uses (or could use) Zoho, e.g. {_examples()}.
- has a fix that can be shown in 2-4 concrete steps (real menus, a real API call, or a real AI prompt).
- uses one of these fix types:
{_solution_types()}
- "GSX problem bank" items are real problems collected by the creator: their "facts" are verified - use them.
Skip {NICHE.get('skip', 'anything without a practical fix')}. Rules: {NICHE.get('safety', '')}.
{evergreen}
Do not repeat these recent problems:
{past}

Never invent Zoho features, menu names, API endpoints, prices or limits. If unsure about an exact menu path,
describe it generally ("in Setup, under Automation").

Return JSON:
{{"angles": [{{
  "story_index": 0,
  "pillar": "trending | ai_agent | lead_flow | dev_api | problem_fix",
  "region": "global | gcc | europe | india",
  "product": "Zoho CRM | Zoho Books | Zoho Flow | Zoho Social | Zoho Creator | Zoho Desk | ... (+ Claude / ChatGPT if used)",
  "app": "main screen to show: {' | '.join(APPS)}",
  "problem": "the pain in one {LANGUAGE} line, specific",
  "fix_type": "{' | '.join(NICHE.get('solution_types', {}).keys()) or 'native'}",
  "solution": "the fix in one line",
  "steps": ["step 1", "step 2", "step 3"],
  "api": "the exact API / endpoint / scope / MCP server / AI prompt used, or null",
  "result": "what the viewer gains (time or money saved, leads not lost)",
  "wow": "the one surprising detail that makes this Short worth sharing",
  "hook": "a scroll-stopping first line in {LANGUAGE}, under 12 words, built on the problem or the news"
}}]}}
Order from best to worst. Best = trending + many businesses have this problem + AI fix + clearest steps.

ITEMS (news, questions, problem bank):
{listing or "(none today)"}"""
    if TRENDING_ONLY:
        prompt = _trending_rules(candidates, n) + "\n\n" + prompt
    angles = ask_json(prompt, temperature=0.5).get("angles", [])
    out = []
    for a in angles:
        i = a.get("story_index")
        if not a.get("problem"):
            continue
        if TRENDING_ONLY and not (isinstance(i, int) and 0 <= i < len(candidates)
                                  and candidates[i].get("type") == "news"):
            print(f"[scout] dropped (not built on a trending news item): {a.get('problem', '')[:90]}")
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
def _real_screens_hint():
    """Real Zoho screenshots available in assets/screens (captured from the creator's own Zoho account)."""
    try:
        from .screens import library
        lib = library()
    except Exception:
        lib = {}
    if not lib:
        return ""
    rows = "\n".join(f'  - "{k}": {v.get("about", "")} (clickable: {", ".join(v.get("targets", {}).keys()) or "-"})'
                     for k, v in list(lib.items())[:60])
    return ("REAL SCREENSHOTS you can use (prefer them when one fits the step): put its key in \"real\" and the "
            f"clickable label in \"click\".\n{rows}\n")


def write_script(angle):
    if not IS_ZOHO:  # niche switch
        return _niche().write_script(angle)
    lo, hi = SCRIPT_WORDS
    s = angle.get("story")
    if s and TRENDING_ONLY and s.get("type") == "news" and not s.get("facts_checked"):
        facts = news_facts(s)
        s["facts_checked"] = True  # the same dict goes to the QA agent -> it checks against the facts too
        if facts:
            s["summary"] = f"VERIFIED FACTS (Google Search):\n{facts}\n\nRSS: {s.get('summary', '')}"[:3200]
    if s and s.get("source") == "GSX problem bank":
        source = f"SOURCE: the creator's problem bank (verified facts):\n{s['title']}\n{s['summary']}"
    elif s and TRENDING_ONLY and s.get("type") == "news":
        source = (f"SOURCE = TRENDING ZOHO NEWS ({s.get('age_hours', '?')} hours old, {s.get('publishers', 1)} "
                  f"publishers): {s['title']} - {s['source']}\n"
                  f"{s['summary']}\nThe HOOK must open on this news (what just happened), then show what it means "
                  f"for a Zoho business and how to use / handle it in Zoho today. State only facts from this news.\n"
                  f"SCREENS (11 Nov 2026, Gaurav): every screen shows THE PRODUCT OF THIS SHORT (a Zoho Books Short = "
                  f"Zoho Books screens, a CRM Short = CRM screens). Use a REAL screenshot ('real': key from the list "
                  f"of real screenshots) whenever one of that product fits the step; else that product's own app "
                  f"page (app = the product). NEVER a Zoho Flow 'flow' chain unless the Short is about Zoho Flow, and "
                  f"never a screen of a different Zoho app. Button / menu names only when they are in the facts or in "
                  f"the real screenshot - never invent one.")
    elif s:
        source = f"SOURCE (the question/news this came from): {s['title']} - {s['source']}\n{s['summary']}"
    else:
        source = "SOURCE: evergreen problem, no news source. Do not mention any news."
    prompt = f"""Write ONE YouTube Short script for "{CHANNEL_NAME}" in natural spoken {LANGUAGE}.
The audience is global (Middle East, Europe, US, India): plain international English, no Indian slang, amounts
in a neutral way (or USD/AED/EUR), no country-specific jokes.
The video switches between the creator's lip-synced AI avatar and the real app screens:
HOOK / PROBLEM / RESULT lines show the presenter talking to camera (keep them SHORT: they cost video credits);
FIX and every STEP line show the screen where that action happens (the Zoho app, the AI chat, the API call or
the code), with the exact button / field / line highlighted while the voice says it.
So every STEP must be ONE concrete action (where to go, what to click, what to type, which endpoint to call),
and its "screen" must show exactly that.

THE ANGLE
Pillar: {angle.get('pillar')}
Product: {angle.get('product')}
Main screen: {angle.get('app')}
Problem: {angle.get('problem')}
Fix type: {angle.get('fix_type')}
Solution: {angle.get('solution')}
Steps: {json.dumps(angle.get('steps', []), ensure_ascii=False)}
API / prompt: {angle.get('api')}
Result: {angle.get('result')}
Wow detail: {angle.get('wow')}
Hook idea: {angle.get('hook')}

{source}

STRUCTURE: HOOK (the problem or the news as a punch, max 10 words) -> PROBLEM (ONE short line, max 14 words) ->
FIX (1 line, name the tool: e.g. "Connect Claude to Zoho CRM with Zoho's MCP server") ->
STEP 1..4 (each one clear action - the screen part is the heart of the video, give it the time; say the wow
detail in one of the steps) -> RESULT (ONE short line, max 14 words, a soft close like "set it up once and
your CRM works for you").
NO CTA line: never ask to follow, like or subscribe. No greeting, no intro.

RULES
- {lo}-{hi} words total in "say". Short sentences. "say" is Roman-script {LANGUAGE}.
- {_LANG_RULES.get(LANGUAGE, _LANG_RULES['English'])}
- "card": 2-7 word on-screen text for that line, e.g. "CRM > Setup > Workflow Rules" or "POST /crm/v8/Leads/upsert".
- "screen" (FIX and every STEP line) - pick what the viewer must SEE:
  * a Zoho app page: "app" one of {', '.join(a for a in APPS if a not in ('claude', 'chatgpt', 'api', 'code'))};
    "view" list | form | settings; real menu names of THAT app only; 2-5 rows/fields; realistic international
    sample data (company names like "Al Noor Trading", "Berlin Logistics GmbH", "Sharma Exports").
  * an AI chat (Claude / ChatGPT connected to Zoho): "app" claude | chatgpt, "view" "chat",
    "messages": [["user", "the exact prompt"], ["assistant", "short answer / what it did"]], "tool": "the MCP
    tool or connector it used, e.g. Zoho CRM - Data Insights".
  * an API call: "app" "api", "view" "api", "method", "url" (real Zoho endpoint with YOUR_DOMAIN placeholders),
    "headers": [["Authorization", "Zoho-oauthtoken ****"]], "body": short JSON text, "response": short JSON text.
  * code (Deluge / widget JS / HTML): "app" "code", "view" "code", "language", "code": max 14 short lines.
  * a Zoho Flow / automation chain: "app" "flow", "view" "flow", "nodes": ["Trigger: ...", "AI: ...", "Action: ..."].
  "click": EXACT text of the button / field / row cell / node / code token to highlight (must appear on that screen).
  "tip": max 8 words.
{_real_screens_hint()}- Never invent Zoho features, menus, endpoints, prices or limits. If unsure of a menu name, say it generally.
- {NICHE.get('safety', '')}
- If the fix needs code (Deluge function, widget, HTML page, API call), put WORKING, minimal, commented code in
  "code". Use placeholders like YOUR_ORG_ID / YOUR_DOMAIN / YOUR_API_KEY, never real keys. Otherwise null.

Return JSON:
{{
 "title": "YouTube title, max 70 chars, problem/fix led, honest, may name the trending tool (Claude, ChatGPT, AI agent)",
 "hook_text": "max 6 words shown big at the top of the video",
 "thumb_text": "3-6 words for the thumbnail cover (the first second): the news or the problem as a caption, e.g. 'Zoho *Analytics* got AI agents' - put the 1-2 key words in *stars*",
 "app_label": "short label for the top tag, e.g. 'Zoho CRM + Claude' or 'Zoho Flow AI'",
 "lines": [{{"beat": "HOOK|PROBLEM|FIX|STEP 1|STEP 2|STEP 3|STEP 4|RESULT", "say": "Roman text",
            "tts": "text for the voice engine", "card": "on-screen text",
            "screen": null or (for FIX / STEP lines) {{"app": "...", "view": "...", "path": ["...", "..."],
                       "heading": "page title", "columns": ["..."], "rows": [["..."]],
                       "fields": [["Field label", "sample value"]], "toggles": [["Option label", true]],
                       "messages": [["user", "..."], ["assistant", "..."]], "tool": "...",
                       "method": "POST", "url": "...", "headers": [["...", "..."]], "body": "...", "response": "...",
                       "language": "deluge", "nodes": ["..."], "real": null,
                       "click": "EXACT text to highlight", "tip": "max 8 words"}}}}],
 "api": {{"name": "what it is", "endpoint": "method + URL or MCP server / Flow app", "scope": "OAuth scope if any",
          "docs": "official docs page title"}} or null,
 "code": {{"language": "deluge|html|javascript|json|bash", "filename": "...", "content": "...",
          "where_to_paste": "exact place in Zoho"}} or null,
 "test_before_recording": ["what to check in your own Zoho account"],
 "description": "2-3 lines: problem, fix, steps summary",
 "tags": ["10 short tags, include the trending tool names"]
}}"""
    return ask_json(prompt, temperature=0.8)


# ---------------------------------------------------------------- 3. Reviewer
def review_script(script, angle):
    lo, hi = SCRIPT_WORDS
    wc = word_count(" ".join(l.get("say", "") for l in script.get("lines", [])))
    if not IS_ZOHO:  # niche switch
        try:
            fixed = ask_json(_niche().review_prompt(script, angle, wc), temperature=0.2)
        except Exception as e:
            print(f"[review] skipped: {e}")
            return script
        return fixed if fixed.get("lines") else script
    prompt = f"""You are the strict editor of a solo {LANGUAGE} YouTube Short about {NICHE['topic']}.
Fix the JSON script below. Checklist:
1. FACTS: no invented Zoho features, menus, API endpoints, prices or limits. Soften anything you are not sure about.
2. STEPS: each step is a concrete action (what to open / click / type / call). Rewrite vague steps.
3. LENGTH: total words in "say" must be {lo}-{hi} (now {wc}). Cut filler, keep hook and steps; remove any CTA / follow line.
4. HOOK: first line is a punchy problem statement under 12 words. No greeting.
5. CODE / API: if present, it must be minimal, correct and safe (no real keys, no deleting data). Fix bugs.
6. SCREENS: every FIX / STEP screen shows the app, chat, API call or code the line talks about, and its "click"
   text really appears on that screen.
7. Roman-script {LANGUAGE} in "say"; every line keeps "beat", "say", "tts" and "card". {NICHE.get('safety', '')}
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
def _news_qa_rules(angle):
    """10 Nov 2026: in trending mode the QA agent sees the news the Short is built on and checks it against it.
    (First trending run: the news was about Zoho CAMPAIGNS, the script said Zoho Marketing Automation, invented
    menus and a '40% more engagement' number that is in no source - QA could not catch it without the news.)"""
    s = angle.get("story") or {}
    if not (TRENDING_ONLY and s.get("type") == "news"):
        return ""
    return f"""- THE NEWS this Short is built on is below. Reject if the script names a different Zoho product than the
  news (e.g. the news is about Zoho Campaigns but the script says Zoho Marketing Automation)
- reject if it states ANY number, percentage, price, date or result ("increase engagement by 40%") that is not
  written in the news text below - results must be described without invented numbers
- reject if a menu / button name for a NEW feature from the news is not in the news text and you are not sure it
  exists: then the step must be described generally ("open the new AI agent workflows in Campaigns")
- reject if the hook does not clearly say what Zoho just launched / changed
- reject if a Zoho app screen shows a menu path or button for the NEW feature that is not in the facts below or in
  a real screenshot
- reject if any screen is NOT the product of this Short (e.g. a Zoho Flow chain or a CRM page in a Zoho Books Short)
NEWS ({s.get('age_hours', '?')} hours old): {s.get('title', '')} - {s.get('source', '')}
{s.get('summary', '')[:900]}
"""


def qa_script(script, angle):
    """A second, independent agent grades the script. Returns {"approved": bool, "issues": [...]}"""
    lo, hi = SCRIPT_WORDS
    if not IS_ZOHO:  # niche switch: same gate logic, Claude-wealth rules
        out = ask_json(_niche().qa_prompt(script, angle), temperature=0.1)
        return {"approved": bool(out.get("approved")) and int(out.get("score") or 0) >= 7,
                "score": out.get("score"), "issues": out.get("issues") or []}
    prompt = f"""You are the quality gate of "{CHANNEL_NAME}", a {LANGUAGE} YouTube Shorts channel about
{NICHE['topic']}. Nobody else reviews this script before it is published, so be strict.

Reject (approved=false) if ANY of these is true:
- it states a Zoho feature, menu, API endpoint, price or limit that you are not confident exists today
- a step is vague (viewer would not know what to click / type / call)
- the code or API call (if any) has a bug, uses real keys, or could delete/overwrite data
- total words in "say" outside {lo}-{hi}, or the first line is not a punchy problem hook
- anything misleading, clickbait, or against: {NICHE.get('safety', '')}
- it mentions or implies affiliation with Zoho Corporation, Anthropic or OpenAI
{_news_qa_rules(angle)}
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
    for _ in range(30):  # wait until Google has processed the video
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
        for rnd in range(4):  # 429 / 503 are usually temporary -> wait and go again
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
{"If they describe a Zoho / automation problem, thank them and say it may become a Short." if IS_ZOHO else _niche().REPLY_LINE}
Otherwise write ONE short, friendly reply (max 30 words) in the same language as the comment.
No links, no promises, no made-up facts."""
    out = ask_text(prompt)
    return None if (not out or out.strip().upper().startswith("SKIP")) else out[:400]


# ---------------------------------------------------------------- 7. Localizer
_LANG_NAMES = {"ar": "Arabic (Modern Standard, natural for UAE / Saudi viewers)", "de": "German", "fr": "French",
               "es": "Spanish", "hi": "Hindi (Devanagari)", "it": "Italian", "pt": "Portuguese", "nl": "Dutch",
               "tr": "Turkish", "ur": "Urdu"}


def localize(title, description, languages):
    """YouTube localizations: {"ar": {"title": ..., "description": ...}, ...}. Empty dict if it fails."""
    langs = [l for l in languages if l]
    if not langs:
        return {}
    want = ", ".join(f'"{l}" = {_LANG_NAMES.get(l, l)}' for l in langs)
    prompt = f"""Translate this YouTube Short title and description for viewers in other countries: {want}.
Keep product and brand names in English ({"Zoho, Zoho CRM, Zia, Claude, ChatGPT, OpenAI, MCP, API, Deluge, Flow" if IS_ZOHO else _niche().BRANDS}),
keep menu paths, code, URLs and hashtags exactly as they are. Title max 95 characters and keep " #Shorts" at
the end. Natural, native wording, not word-by-word.

TITLE: {title}
DESCRIPTION:
{description[:3500]}

Return JSON: {{"<language code>": {{"title": "...", "description": "..."}}, ...}} for exactly these codes: {langs}"""
    try:
        out = ask_json(prompt, temperature=0.2, retries=4)
    except Exception as e:
        print(f"[localize] skipped: {e}")
        return {}
    res = {}
    for l in langs:
        v = out.get(l) if isinstance(out, dict) else None
        if isinstance(v, dict) and v.get("title"):
            t = str(v["title"]).replace("<", "‹").replace(">", "›")[:100]
            d = str(v.get("description") or description).replace("<", "‹").replace(">", "›")[:4900]
            res[l] = {"title": t, "description": d}
    print(f"[localize] {', '.join(res) or 'none'}")
    return res
