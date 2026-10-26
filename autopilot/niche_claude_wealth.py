"""NICHE: claude_wealth (27 Oct 2026) - "how real people earn with Claude" + "Claude's real problems".

This file is the second branch of the niche switch (channel.yaml -> active_niche). The Zoho niche never imports it:
writer.py / main.py / flow.py / composer.py / screens.py / benchmark.py run their original Zoho code when
config.IS_ZOHO is True and call into here otherwise.

Same pipeline, same presenter, same editor and QA strictness - only WHAT the agents write changes:
  scout   -> picks the next Short by niche.rotation (4 x wealth, then 1 x problems)
  script  -> HOOK / PROBLEM (face) -> FIX + STEPS (screens: Claude chat, Skill file, Claude Code, tool chain,
             numbers card) -> RESULT with the honest catch (face)
  QA      -> rejects hype, guaranteed income, trading / investment advice, invented Claude features
"""
import json

from .config import CHANNEL_NAME, CHANNEL_HANDLE, LANGUAGE, NICHE, PILLARS, SCRIPT_WORDS, EVERGREEN_FALLBACK, \
    DISCLAIMER, HASHTAGS

# what the screen part of a Short can show in this niche (autopilot/screens.py draws each one)
APPS = ("claude", "code", "flow", "api", "notes")
ROTATION = [str(x).lower() for x in (NICHE.get("rotation") or ["wealth"])]

SAFETY = NICHE.get("safety", "")
HARD_RULES = f"""HARD RULES (a Short that breaks one is never published):
- No financial, investment, trading, banking or tax advice. Never name a stock, coin, bet or trading strategy as a
  way to earn. Trading / banking appear ONLY as "Claude helps you build or research a tool - YOU decide - you can
  lose money", or as myth-busting.
- Never promise or imply guaranteed income. Every money number names who reported it ("one creator reports...",
  "typical asking price...") and the Short says results vary. No "passive income", no "get rich".
- Only Claude features that really exist (Claude chat, Projects, Skills / SKILL.md, artifacts, connectors / MCP,
  Claude Code in the terminal, the Claude API). If unsure of an exact menu name, describe it generally.
- Never show real API keys, client data, bank balances or earnings dashboards. Never claim to be Anthropic.
- {SAFETY}"""


def _ask(prompt, temperature):
    from .writer import ask_json
    return ask_json(prompt, temperature=temperature)


def kind_of(pillar):
    p = PILLARS.get(str(pillar or ""), {}) or {}
    return str(p.get("kind") or ("problems" if pillar == "problems" else "wealth")).lower()


def needed_kinds(start, n):
    """The next n kinds from the rotation (e.g. wealth, wealth, wealth, wealth, problems, wealth, ...)."""
    return [ROTATION[(start + i) % len(ROTATION)] for i in range(n)]


def order_angles(angles, kinds):
    """Puts the scout's angles in rotation order: slot i gets the best angle of kind kinds[i]; leftovers follow."""
    pool, out = list(angles), []
    for k in kinds:
        a = next((x for x in pool if kind_of(x.get("pillar")) == k), None)
        if a is not None:
            pool.remove(a)
            out.append(a)
    return out + pool


def _pillars():
    return "\n".join(f'   - "{k}" ({v.get("kind", "wealth")}, weight {v.get("weight", 1)}): {v.get("about", "")}'
                     for k, v in PILLARS.items())


def _solution_types():
    return "\n".join(f'   - "{k}": {v}' for k, v in (NICHE.get("solution_types") or {}).items())


# ---------------------------------------------------------------- 1. Scout
def scout(candidates, n, past_problems, kinds=None):
    kinds = kinds or needed_kinds(0, n)
    listing = "\n".join(
        f"[{i}] (trend {c.get('trend', 0)}) {c['title']} | {c['source']} | {c['summary'][:700]}"
        for i, c in enumerate(candidates))
    past = "\n".join(f"- {p}" for p in past_problems[-60:]) or "- (none yet)"
    evergreen = (f"If fewer than {n} items fit, ADD strong angles you are sure about with story_index -1 "
                 "(no invented numbers in them)." if EVERGREEN_FALLBACK else "Only use the items below.")
    prompt = f"""You are the research lead of "{CHANNEL_NAME}", a {LANGUAGE} YouTube Shorts channel about
{NICHE['topic']}, for {NICHE['audience']}. Each Short is presented by the channel's AI avatar presenter.
Our promise: {NICHE['promise']}

We need exactly these Shorts, in this order (kind of each): {json.dumps(kinds)}
- "wealth" = ONE real way people earn with Claude, shown as a workflow the viewer can copy today.
- "problems" = ONE real problem / limit / myth of earning with Claude, and how pros handle it.
Then add 2 spare angles of the same kinds.

Pillars (the weight = how often inside its kind):
{_pillars()}

A good angle:
- a specific, relatable situation, e.g. {"; ".join(f'"{p}"' for p in NICHE.get("good_problems", []))}
- a method that can be SHOWN in 2-4 concrete steps on screen (the exact prompt, the Skill file, the Claude Code
  command, the trigger -> Claude -> action chain, or an honest numbers card)
- uses one of these Claude tools:
{_solution_types()}
- has the honest catch (what it costs, where it breaks, who it does NOT work for)
- "GSX problem bank" items are researched: use their facts and keep the "who reported it" with every number;
  items with an "order" are the creator's planned sequence - prefer them in that order.
- trending items (Claude launches this week) are great hooks if they lead to a real earning method.
Skip: {NICHE.get('skip', '')}.
{HARD_RULES}
{evergreen}
Do not repeat these recent topics:
{past}

Return JSON:
{{"angles": [{{
  "story_index": 0,
  "pillar": "{' | '.join(PILLARS)}",
  "kind": "wealth | problems",
  "region": "global | india | gcc | europe | us",
  "product": "the Claude tool(s) used, e.g. 'Claude Skills + Stripe' or 'Claude Code'",
  "app": "main screen to show: {' | '.join(APPS)}",
  "problem": "the situation / pain in one {LANGUAGE} line, specific",
  "fix_type": "{' | '.join((NICHE.get('solution_types') or {}).keys())}",
  "solution": "the method in one line",
  "steps": ["step 1", "step 2", "step 3"],
  "api": "the exact prompt / Skill / command / chain used, or null",
  "numbers": "the honest money numbers WITH who reported them, or null if none are sourced",
  "catch": "the honest limitation / cost / risk in one line",
  "result": "what the viewer can realistically get (no guarantees)",
  "wow": "the one surprising detail that makes this worth sharing",
  "hook": "a scroll-stopping first line in {LANGUAGE}, under 12 words, curiosity not hype"
}}]}}
First the angles for the requested kinds, in that order. Best = real + trending + clearest steps + honest.

ITEMS (news, community posts, problem bank):
{listing or "(none today)"}"""
    angles = _ask(prompt, 0.5).get("angles", [])
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
        a["kind"] = kind_of(a.get("pillar")) if a.get("pillar") in PILLARS else str(a.get("kind") or "wealth")
        out.append(a)
    return order_angles(out, kinds)


# ---------------------------------------------------------------- 2. Scriptwriter
def write_script(angle):
    lo, hi = SCRIPT_WORDS
    s = angle.get("story")
    if s and s.get("source") == "GSX problem bank":
        source = f"SOURCE: the creator's research bank (verified facts - keep 'who reported it'):\n{s['title']}\n{s['summary']}"
    elif s:
        source = f"SOURCE (the post / news this came from): {s['title']} - {s['source']}\n{s['summary']}"
    else:
        source = "SOURCE: evergreen angle, no news source. Do not mention any news and use no unsourced numbers."
    is_problem = str(angle.get("kind")) == "problems"
    shape = ("HOOK (the myth / problem as a punch, max 10 words) -> PROBLEM (ONE short line: what goes wrong, max 14 "
             "words) -> FIX (1 line: how pros handle it) -> STEP 1..4 (the exact checks / settings / prompts on screen) "
             "-> RESULT (ONE short line, max 14 words: the takeaway)") if is_problem else (
             "HOOK (curiosity, max 10 words, no hype) -> PROBLEM (ONE short line: the situation, max 14 words) -> "
             "FIX (1 line: the method, name the Claude tool) -> STEP 1..4 (the workflow on screen: the exact prompt, "
             "Skill, command or chain; one step shows the honest numbers card with who reported them) -> RESULT "
             "(ONE short line, max 14 words: realistic outcome + the catch, e.g. 'works if you already have an "
             "audience - start with one client')")
    prompt = f"""Write ONE YouTube Short script for "{CHANNEL_NAME}" in natural spoken {LANGUAGE}.
Audience: {NICHE['audience']}. Plain international English, friendly and smart, no slang, amounts in USD
(or "about 8 lakh rupees" only if the source gives INR). It must feel like a smart friend showing what really
works, not a guru selling a course.
The video switches between the creator's lip-synced AI avatar and screens:
HOOK / PROBLEM / RESULT lines show the presenter talking to camera (keep them SHORT: they cost video credits);
FIX and every STEP line show a screen where that action happens, with the exact text highlighted while the
voice says it. So every STEP is ONE concrete action and its "screen" shows exactly that.

THE ANGLE
Kind: {angle.get('kind')}   Pillar: {angle.get('pillar')}   Tool: {angle.get('product')}
Situation: {angle.get('problem')}
Method: {angle.get('solution')}
Steps: {json.dumps(angle.get('steps', []), ensure_ascii=False)}
Prompt / Skill / command: {angle.get('api')}
Numbers (with source): {angle.get('numbers')}
Catch: {angle.get('catch')}
Result: {angle.get('result')}
Wow detail: {angle.get('wow')}
Hook idea: {angle.get('hook')}

{source}

STRUCTURE: {shape}.
NO CTA line: never ask to follow, like or subscribe. No greeting, no intro.

RULES
- {lo}-{hi} words total in "say". Short sentences. "say" is Roman-script {LANGUAGE}. "tts" = the same as "say".
- "card": 2-7 word on-screen text for that line, e.g. "Skill = one SKILL.md file" or "$99 x bundle".
- "screen" (FIX and every STEP line) - pick what the viewer must SEE:
  * a Claude chat: "app" "claude", "view" "chat", "messages": [["user", "the exact prompt to copy"],
    ["assistant", "short realistic answer"]], "tool": "the Claude feature used, e.g. 'Project: Client voice' or
    'Skill: youtube-script'".
  * a file / Skill / code / terminal: "app" "code", "view" "code", "language" (markdown | bash | python | json),
    "heading" (file name, e.g. "SKILL.md" or "Terminal - Claude Code"), "code": max 14 short lines.
    A Skill file starts with front matter: name + description, then short instructions.
  * a tool chain: "app" "flow", "view" "flow", "heading", "nodes": ["Trigger: ...", "Claude: ...", "Action: ..."].
  * an API call: "app" "api", "view" "api", "method", "url" (real Anthropic API URL), "headers"
    [["x-api-key", "****"]], "body", "response".
  * a numbers / checklist card: "app" "notes", "view" "notes", "heading", "rows": [["label", "value"], ...]
    (max 5 rows; every money row ends with its source, e.g. ["Bundle price", "$99 (creator's report)"]).
  "click": EXACT text to highlight (must appear on that screen). "tip": max 8 words.
{HARD_RULES}
- If the method needs a file (Skill, prompt, small script), put a WORKING, minimal version in "code" with
  placeholders like YOUR_API_KEY - never real keys. Otherwise null.

Return JSON:
{{
 "title": "YouTube title, max 70 chars, curiosity + honest (no 'guaranteed', no '$10k/month easy'), may name Claude",
 "hook_text": "max 6 words shown big at the top of the video",
 "app_label": "short label for the top tag, e.g. 'Claude Skills' or 'Claude Code'",
 "lines": [{{"beat": "HOOK|PROBLEM|FIX|STEP 1|STEP 2|STEP 3|STEP 4|RESULT", "say": "Roman text",
            "tts": "text for the voice engine", "card": "on-screen text",
            "screen": null or (for FIX / STEP lines) {{"app": "...", "view": "...", "heading": "...",
                       "rows": [["...", "..."]], "messages": [["user", "..."], ["assistant", "..."]], "tool": "...",
                       "method": "POST", "url": "...", "headers": [["...", "..."]], "body": "...", "response": "...",
                       "language": "markdown", "code": "...", "nodes": ["..."],
                       "click": "EXACT text to highlight", "tip": "max 8 words"}}}}],
 "api": {{"name": "the Claude tool", "endpoint": "prompt / Skill / command / chain in one line", "scope": null,
          "docs": "official docs page title"}} or null,
 "code": {{"language": "markdown|bash|python|json", "filename": "...", "content": "...",
          "where_to_paste": "where it goes (e.g. a Skill folder, Claude Project instructions)"}} or null,
 "sources": ["who reported each number (name + site)"],
 "description": "2-3 lines: situation, method, the catch",
 "tags": ["10 short tags, include Claude and the method"]
}}"""
    return _ask(prompt, 0.8)


# ---------------------------------------------------------------- 3. Reviewer + QA gate
def review_prompt(script, angle, wc):
    lo, hi = SCRIPT_WORDS
    return f"""You are the strict editor of a solo {LANGUAGE} YouTube Short about {NICHE['topic']}.
Fix the JSON script below. Checklist:
1. FACTS: only real Claude features; every money number keeps who reported it; remove any number without a source.
2. HONESTY: no hype, no guaranteed income, the catch is said out loud (RESULT line or a step).
3. STEPS: each step is a concrete action (what to open / type / run / connect). Rewrite vague steps.
4. LENGTH: total words in "say" must be {lo}-{hi} (now {wc}). Cut filler, keep hook and steps; remove any CTA / follow line.
5. HOOK: first line is a punchy curiosity / problem line under 12 words. No greeting.
6. CODE / SKILL / API: minimal, correct, safe (no real keys, nothing that spends money or deletes data).
7. SCREENS: every FIX / STEP screen shows what its line talks about, and its "click" text really appears on it.
8. Roman-script {LANGUAGE} in "say"; every line keeps "beat", "say", "tts" and "card".
{HARD_RULES}
Return the corrected JSON only, same structure.

ANGLE: {json.dumps({k: v for k, v in angle.items() if k != 'story'}, ensure_ascii=False)}

SCRIPT:
{json.dumps(script, ensure_ascii=False)}"""


def qa_prompt(script, angle):
    lo, hi = SCRIPT_WORDS
    return f"""You are the quality gate of "{CHANNEL_NAME}", a {LANGUAGE} YouTube Shorts channel about
{NICHE['topic']}. Nobody else reviews this script before it is published, so be strict.

Reject (approved=false) if ANY of these is true:
- it gives financial / investment / trading / banking / tax advice, names a stock, coin or bet, or presents
  trading as a way to earn (myth-busting a trading story is fine)
- it promises or implies guaranteed income, uses hype words ("passive income", "easy money", "get rich"), or shows
  a money number without saying who reported it
- it states a Claude / Anthropic feature, price or limit you are not confident exists today
- a step is vague (viewer would not know what to type / run / click)
- the code / Skill / API call (if any) has a bug, uses real keys, or could spend money or delete data
- the honest catch is missing
- total words in "say" outside {lo}-{hi}, or the first line is not a punchy hook
- anything misleading, clickbait, or it mentions or implies affiliation with Anthropic
- it could break YouTube rules (spam, scams, deceptive practices) or teach something that breaks a platform's terms

Return JSON: {{"approved": true|false, "score": 1-10, "issues": ["specific problem + how to fix"]}}

ANGLE: {json.dumps({k: v for k, v in angle.items() if k != 'story'}, ensure_ascii=False)}
SCRIPT: {json.dumps(script, ensure_ascii=False)}"""


REPLY_LINE = ("If they describe a way they earn (or fail to earn) with Claude / AI, thank them and say it may become a "
              "Short. Never give investment, trading, banking or tax advice and never promise income - answer SKIP "
              "if they ask for that.")
BRANDS = "Claude, Claude Code, Claude Skills, Anthropic, MCP, API, Stripe, Gumroad, n8n, Make, Zapier, YouTube"


# ---------------------------------------------------------------- 4. YouTube metadata
def build_title(sc, yt_safe):
    t = (sc.get("title") or f"{CHANNEL_NAME} - earn with Claude").replace("#Shorts", "").strip()
    return yt_safe((t[:88] + " #Shorts").strip())


def build_description(sc, angle, yt_safe, ai_disclosure):
    lines = [(sc.get("description") or "").strip(), ""]
    steps = angle.get("steps") or []
    if steps:
        lines += [f"{i + 1}. {s}" for i, s in enumerate(steps)] + [""]
    api = sc.get("api")
    if isinstance(api, dict) and (api.get("endpoint") or api.get("name")):
        lines += ["Tool used:"] + [f"- {k}: {api[k]}" for k in ("name", "endpoint", "docs") if api.get(k)] + [""]
    code = sc.get("code")
    if isinstance(code, dict) and code.get("content") and len(code["content"]) < 2500:
        lines += [f"{code.get('filename') or 'File'} ({code.get('language', '')}) - {code.get('where_to_paste', '')}:",
                  code["content"], ""]
    src = [str(x) for x in (sc.get("sources") or []) if str(x).strip()]
    if angle.get("catch"):
        lines += [f"The catch: {angle['catch']}", ""]
    if src:
        lines += ["Sources for the numbers:"] + [f"- {x}" for x in src[:5]] + [""]
    lines.append(f"Real ways to earn with AI, no hype - follow {CHANNEL_HANDLE}")
    story = angle.get("story")
    if story and str(story.get("link", "")).startswith("http"):
        lines += ["", f"What inspired this: {story['link']}"]
    lines += ["", ai_disclosure]
    if DISCLAIMER:
        lines.append(DISCLAIMER)
    lines += ["", " ".join("#" + h.lstrip("#").replace(" ", "") for h in HASHTAGS)]
    return yt_safe("\n".join(lines))


def app_label(sc, specs):
    import html as h
    lab = str(sc.get("app_label") or "").strip()
    if not lab and specs:
        lab = {"claude": "Claude", "code": "Claude Code", "flow": "Claude + automation", "api": "Claude API",
               "notes": "Claude income"}.get(specs[0].get("app", ""), "Claude")
    return h.escape(lab[:28] or "Claude")


# ---------------------------------------------------------------- 5. QA texts for benchmark.py
QA_NICHE = "English 'earn with Claude' Shorts"
QA_LEARN = "English 'how people earn with Claude' Shorts with an AI avatar of the creator + Claude / tool screens"
QA_SCREEN_PART = "screen"
QA_SCREENS = ("the Claude chat / Skill file / Claude Code / tool-chain / numbers screens show what is being said at "
              "that moment, the exact text is highlighted, readable on a phone")
QA_STORY = ("hook in the first 2 s, the method is real and complete, money numbers say who reported them, the catch is "
            "said, no hype or financial advice, the video ends cleanly (no abrupt cut)")
QA_VALUE = "the viewer learns a real, honest way to earn with Claude they can try, including the catch"
