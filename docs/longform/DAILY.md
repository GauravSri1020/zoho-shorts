# DAILY ROBOT - what the daily Claude "brain" does (Gaurav's order, 15 Nov 2026; UPDATED 20 Nov 2026)

## 22 Nov 2026 - Gaurav (this file is back to the 20 Nov MORNING version; the 20 Nov night "engine only" lines are gone)
- ZOHO SHORTS (2 per day) come from the engine on `main` (autopilot/): research (trending Zoho news, Middle East
  first: UAE / Saudi / Gulf) -> script -> Flow clip HOOK + PROBLEM -> real recorded Zoho screens / screenshots that
  walk through the steps -> Flow clip RESULT (3 Flow clips per Short). NEVER faceless. The brain does NOT write Zoho Shorts.
- TRENDING NEWS SHORT (Nvidia style, our best performer) - 22 Nov night, Gaurav: "Nvidia wale whiteboard pe cartoon
  wali cheezein laga ke, bina Flow ke, free mein". So 1-2 per day as a WHITEBOARD / CARTOON Short: write
  `docs/longform/shorts/<id>.json` ("format": "short", "priority": "news") -> shorts-daily renders (Kokoro voice,
  cartoon guy, stat boards), QA, uploads to the free news slot (13:30 IST first). This LIFTS the 20 Nov ban in point 1
  for trending-news Shorts only (Zoho how-to Shorts stay on the main engine with Flow). Topic = the biggest business /
  tech / AI story people search TODAY (Nvidia, AI companies, big launches, Gulf business news), never a repeat of
  topics-used.md. Example: docs/longform/shorts/s20261122-nvidia-worst-week.json. Legal care: "X reported, citing ...",
  never state an accusation as fact, "not financial advice" for stock stories, 2+ sources (filing / press release first).
- LONG VIDEOS (1 per day, 18:30 IST, uploaded straight to YouTube by longform-daily): Zoho topics AND big trending
  news like Nvidia (latest results, leadership, chips) - pick whichever is trending most that day. Same fact rules.

## 20 Nov 2026 changes (Gaurav: "next level", monetization fast) - these override older lines below
1. SHORTS = FLOW AVATAR ONLY. No cartoon / Kokoro Shorts any more (he deleted the 6 of 18-19 Nov). Do NOT write
   `docs/longform/shorts/*.json` or `queue/shorts/*.json`. Instead write 2-3 Flow Short specs per day
   (`docs/longform/flow-specs/<id>.json`, format in flow-specs/README.md) + `docs/longform/flow-queue/<date>.md`.
   A Claude session with Gaurav's Chrome makes the clips in Flow and schedules them.
2. ONE TRENDING NEWS SHORT EVERY DAY: the biggest business / tech / AI story people are searching TODAY (Nvidia
   style - our 2 best videos ever), even when it is not Zoho. Facts: official filing / press release + 2 outlets.
   Plus 1 Zoho / Gulf-compliance avatar Short.
3. SCRIPT-WRITER AGENT: every long video script and every Flow spec is written by the subagent
   `script-writer` (.claude/agents/script-writer.md, Task tool). You (brain) do research + fact table, then hand
   the topic + research file to it. It picks a DIFFERENT structure each time (docs/longform/STRUCTURES.md,
   rotation checked by the validator via `docs/longform/structures-used.md`).
4. Read `docs/longform/CHANNEL_INSIGHTS.md` before choosing topics (what works on this channel).
5. Research sources (wider): Google News, Techmeme, Hacker News front page, Reddit (r/technology, r/business,
   r/stocks, r/Zoho, r/smallbusiness, r/UAE, r/saudiarabia), LinkedIn News "Top stories" / trending posts and
   Zoho's LinkedIn page (public pages via WebFetch; never log in), X/Twitter trending via news coverage,
   Google Trends (IN / AE / SA / US), YouTube search suggestions (what people type), Zoho Community + zoho.com/blog,
   Product Hunt, official regulators (MoF UAE, FTA, ZATCA, GSTN). A trend counts when >= 3 outlets carry it today.
6. GitHub Actions minutes are limited (Free plan 2,000 min / month - ran out on 18 Nov 2026). Keep the brain run
   short: at most ONE test render per day, no 4K test renders, stop after the report.


Gaurav: "2 Shorts + 1 long video EVERY day, automatically - research, make, upload, schedule. Always keep at least
2 days (better a week) ready. Fresh news goes out first; evergreen videos fill the days after. Research must be tight:
no mistake in facts, script or frames. If something fails, at least tell me the next topics."

HOW IT RUNS (no Claude chat, no scheduler in the Claude app, no laptop):
- `main/.github/workflows/daily-robot.yml` (GitHub cron) runs this file every morning with Claude Code
  (anthropics/claude-code-action, secret CLAUDE_CODE_OAUTH_TOKEN = Gaurav's subscription) on a GitHub runner.
- The same workflow runs the KEEPER twice a day (no AI): when less than 3 days are scheduled it moves ready scripts
  from `docs/longform/queue/` into production. So the queue is the safety buffer - keep it full.
- Makers (branch long-videos): `shorts-daily` (9:16 Shorts) and `longform-daily` (16:9 long videos): validate ->
  Kokoro voice -> render -> strict QA -> YouTube (scheduled). A push made with the runner token does NOT start
  workflows, so after pushing always start them yourself:
  `gh workflow run shorts-daily.yml --ref long-videos -f files="docs/longform/shorts/a.json docs/longform/shorts/b.json"`
  `gh workflow run longform-daily.yml --ref long-videos -f request="docs/longform/daily/<id>.json"`
- No Google Flow, no logins, no passwords, nothing in Claude chats or artifacts. The old Gemini Shorts robot on
  `main` keeps running as it is - never change `autopilot/` or other files on `main` from the daily run.

## 0. Start
1. You are in a checkout of branch `long-videos` (git user already set). `git pull`. Read: `CLAUDE.md`, this file,
   `docs/longform/topics-used.md` (never repeat a topic of the last 30 days), the newest files in
   `docs/longform/shorts-failed/`, `docs/longform/failed/`, and count `docs/longform/queue/shorts|long/`.
2. Results so far: `docs/longform/shorts-uploaded/`, `docs/longform/uploaded/` (publish_at = when it goes public).

## 1. Research (WebSearch + WebFetch) - accuracy beats speed
Rank today's candidates (at least 10) in THIS priority order (Gaurav, 15 Nov):
1. ZOHO ECOSYSTEM NEWS, joined to what is trending: Zoho has ~55+ apps (Books, Invoice, Billing, Inventory, Expense,
   Payroll, CRM, Bigin, Desk, Projects, Sign, Social, Campaigns, Marketing Automation, Forms, Analytics, Creator,
   Flow, Cliq, Mail, Workplace, Zoho One, Zia AI ...). Look for: new features / releases (zoho.com/blog, product
   "what's new" pages, help-doc release notes), Zia + AI agents, Zoho + Claude / ChatGPT / MCP servers, pricing and
   licensing changes (what changed, how to buy / upgrade), Zoho partner news (partner programme, audits,
   certifications - e.g. the December partner audit), Zoho events, Zoho in the Middle East / India / Europe.
   Audience = Zoho customers, Zoho partners and people choosing software -> say why it matters to THEM.
2. Tax / compliance updates that hit Zoho users: UAE (MoF, FTA e-invoicing), Saudi (ZATCA waves), India (GST, e-invoice,
   e-way bill), Oman / Bahrain / Qatar, EU (ViDA, Peppol, national e-invoicing), plus follow-ups on topics we already
   covered (new decision, new date, new list) - an update video is good content.
3. Zoho how-to tutorials (evergreen) - one real problem, fixed step by step in a Zoho app.
4. LAST: general trending business news (big tech, AI companies, markets, crypto moves) - only when 1-3 give nothing.
Freshness: news from today / yesterday goes out in the next free slot ("priority": "news"); a week-old item is fine
when it is still relevant (deadline still ahead); evergreen goes to the queue.

Fact rules (CLAUDE.md rule 3 - wrong facts are never uploaded):
- Every number, date, name, price and claim: from an official primary source (government, Zoho's own pages) OR two
  independent reputable outlets. Open the pages (WebFetch) - never write from a search snippet alone.
- Prices / plans: only from Zoho's own pricing page for the region you name, with the date checked.
- Real people: only what the sources say, no opinions, no invented quotes, no photos of real people.
- Zoho steps (menu paths, button names) only from Zoho's own help pages, and only screens that exist in
  `assets/screens/index.yaml` with those exact click targets. If a step cannot be shown on a real screen, show it
  as a board (flow2 / checklist) - never invent a Zoho screen. Screens are from a sample India org: do not show
  India-only settings (GST) for another country.
- Unverifiable -> drop it. Topic falls apart -> next candidate. Write the fact table first (research file).

## 2. Shorts - target: 2 per day scheduled + 6 ready in the queue
- File: `sYYYYMMDD-<slug>.json`, `"format": "short"`. Copy `docs/longform/shorts/s20261115-uae-pdf.json`.
  News Short -> `docs/longform/shorts/` with `"priority": "news"` (earliest free slot incl. 13:30 IST) + dispatch.
  Evergreen Short -> `docs/longform/queue/shorts/` (the keeper schedules it at 07:30 / 21:30 IST when needed).
- 30-48 s spoken (95-150 words), 3-4 scenes, line 1 = the hook (the surprising fact, no "hi guys"), last line = the
  takeaway / where to learn more. Natural English, short sentences, no hype words.
- `headline` max ~8 words with one *highlighted* phrase; `kicker` 2-4 words + date; `source_line` real sources.
- `title` <= 90 chars, search keyword first, no clickbait. `tags` 8-15 real search phrases.
- `description`: summary, sources with URLs + "checked <date>", "General information..." line for tax/legal, the
  AI-disclosure line ("This video uses an AI-generated presenter, voice and animations..."), "Independent channel.
  Not affiliated with or endorsed by Zoho Corporation." when Zoho is named, hashtags.
- `caption_fix`: spoken -> written ("fifty million dirhams" -> "AED 50 million", "B to B" -> "B2B", "C S I D" -> "CSID").
- Check before pushing: `python -m longform.validate F`, then render it and LOOK:
  `python longform/voice.py F /tmp/v && python -m longform.render F --voice /tmp/v --out /tmp/r --scale 1 &&
   python -m longform.vshort build F /tmp/r /tmp/s.mp4 && python -m longform.qa /tmp/s.mp4 --voice /tmp/r/voice.wav --short`
  + contact sheet `ffmpeg -i /tmp/s.mp4 -vf "fps=1/3,scale=270:480,tile=6x2" -frames:v 1 /tmp/c.jpg` -> Read it.
  Text cut off, empty frames, overlaps, wrong facts on screen = fix first.

## 3. Long videos - target: 1 per day scheduled + 3 ready in the queue
- Topic: the strongest universal problem / update from the research, with real Zoho screens where possible.
  id `<slug>`, new. Files: `docs/longform/research/<id>.md` (fact table: fact | value | source URL | official/secondary,
  + "not verified -> not used"), `docs/longform/scripts/<id>.json` (copy `zatca-phase2-zoho-books.json`).
- 7-10 min video = 6.6-11 min spoken (validator), 4-5 chapters, a new scene every 15-40 s, HOOK first (hook2),
  OUTRO last, >= 3 PODCAST scenes for Zoho how-tos. `thumb` (chip, l1/l2/l3 1-2 words each, l2 = keyword in the
  accent colour, pill, pose arms_crossed|open_hands|point_up|point_you|wow, accent colour). Title <= 100 chars,
  keyword first. Description with `{chapters}`, sources, disclaimers.
- Check: validate, voice, `python -m longform.render F --voice V --out R --scale 0.5 --plan-only` (total must be
  7-12 min) + `python -m longform.preview R/plan.json R/stills "" 0` + contact sheet -> Read it. Thumbnail:
  `python -m longform.thumb F /tmp/t.jpg` -> Read it.
- Evergreen -> `docs/longform/queue/long/<id>.json` = `{"id": "<id>", "script": "docs/longform/scripts/<id>.json"}`
  (keeper sets publish_at). Fresh news -> `docs/longform/daily/<id>.json` with `"publish_at"` = next 13:00Z that is
  >= 3 h away and not already taken by another long video, then dispatch longform-daily (one at a time: if a
  longform-daily run is in progress, put it in the queue instead).

## 4. Watch, retry, never weaken QA
- `gh run list --workflow shorts-daily.yml` / `longform-daily.yml`, result folders. On failure:
  `gh run view <id> --log-failed`. Script problem -> fix + dispatch again (max 2 retries) or next topic.
  Code bug -> smallest fix on `long-videos`, never relax a QA check, note it in the report.
- Do not wait for long renders to finish (they take 1-2 h); the next run / the keeper checks them.

## 5. Flow scripts for Gaurav (he opens Flow about once a day)
- Write `docs/longform/flow-queue/YYYY-MM-DD.md`: 2 avatar Short scripts on today's best topics, split into clips of
  <= 8 s (one sentence each) with the Flow prompt per clip (same look as main's Flow prompts: office blazer, medium
  shot, no tilak, natural gestures), plus title/description. A live Claude chat makes them when he opens Flow.

## 6. Report + log (always, also when things failed)
- Append `docs/longform/topics-used.md` (date | type | id | title | status).
- Commit + push everything to `long-videos`.
- GitHub issue titled `Daily report YYYY-MM-DD` (assign the repo owner, short Hinglish): what got scheduled
  (title, link, publish time IST), queue size, failures + why, and the next 5 topic ideas.
  `gh issue create --title ... --assignee GauravSri1020 --body ...`

## Scene kinds (generic - work for any topic). One beat / item per voice line unless noted.
- HOOK `hook2`: `beats` (= number of lines): `{"t":"headline","source","date","text","tag","color"}`,
  `{"t":"stat","value","label","color"}`, `{"t":"title","title","sub","chips":[...]}`,
  `{"t":"guy","pose","prop","text","stamp","stamp_color","color"}`.
- CARTOON `story`: `beats` (= lines) like the guy beat above (`t` optional). Optional `title`.
- BOARD/CARTOON `stat`: `title`, `stats` (1-3: `{"value","label","note","color"}`; numbers count up), `footer`.
- BOARD `headline`: `title`, `items` (1-3: `{"source","date","text","color"}`).
- BOARD `dates`: `title`, `items` (1-6: `{"date","label","big":true?}`).
- BOARD `flow2`: `title`, `steps` (2-5: `["Title","short note"]`), `footer` (spread over the lines).
- BOARD `compare`: `title`, `left/right: {"title","items"}`, `cues: [[line, "L0", "R0"], [line, "L1", "R1"], ...]`.
- BOARD `checklist`: `title`, `items` (= lines, max 6).
- CARTOON `celebrate2`: `top`, `big`, `sub`.
- CHAPTER: `{"num": n, "title": "..."}` (one line: "Chapter n. Title.").
- OUTRO `outro`: `next` (next video), `badge`, `badge_sub`, `note` (2 lines: subscribe + a caution line).
- PODCAST (real Zoho screen): `path` (breadcrumbs), `actions`: `{"cue": line, "screen": "books/<name>", "target": "<exact
  target from index.yaml>", "zoom": 1.4-2.0, "at": 0-1}`; first action sets a screen.
- props: doc, einvoice, envelope, laptop, clock, calendar{top,big,sub}, server{label}, gov{label}, office{label}, coins,
  chart_up, chart_down, warning, phone{label}, robot, magnifier, lock, stack.
- poses: stand, walk, carry, point, cheer, worried, shrug, type, run, present. Colors: teal, navy, amber, coral, sky,
  green, red, lav, mute.
- UAE-only kinds (hook, old_way, five_corner, fourteen_days, penalty, celebrate, badge, formula, record, timeline, flow)
  are drawn for the UAE video only - the validator blocks them elsewhere.
