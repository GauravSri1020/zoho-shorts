# DAILY ROBOT - what the scheduled Claude run does every morning (Gaurav's order, 15 Nov 2026)

Gaurav: "2 Shorts + 1 long video EVERY day, automatically - research, make, upload, schedule. If the news is wrong or
missing, take other trending news; if there is none, make a tutorial. If something fails, at least tell me the next topics."

Everything runs WITHOUT Gaurav's browser: no Google Flow, no logins, no passwords. Shorts + long videos are rendered by
GitHub Actions on branch `long-videos` (Kokoro voice, geometric cartoons, whiteboards, real Zoho screens, the round
presenter loop). The old Gemini Shorts robot on `main` keeps running as it is - never change `autopilot/` or `main`'s
workflows from the daily run.

## 0. Start (5 min)
1. `add_repo` GauravSri1020/zoho-shorts (access push). Clone, `git fetch origin main long-videos longform-previews`,
   work on `long-videos`. Push with `git -c push.negotiate=true push`.
2. Read: `CLAUDE.md` (main), the last 60 lines of `docs/HISTORY.md` (main), this file, `docs/longform/topics-used.md`
   (never repeat a topic from the last 30 days), the newest files in `docs/longform/shorts-failed/` + `docs/longform/failed/`.
3. CLAUDE.md rule 1: push a backup branch `backup-YYYY-MM-DD-daily` from `origin/long-videos` before changing anything.

## 1. Research (WebSearch, ~20 min) - accuracy beats speed
Find today's candidates in this order and keep a ranked list of at least 8:
1. Zoho news (zoho.com/blog, Zoho press releases, product updates) from the last 7 days.
2. Tax / compliance changes that hit small businesses using accounting software: UAE (MoF, FTA), Saudi (ZATCA),
   India (GST council / CBIC / GSTN), EU (ViDA, national e-invoicing), plus any country with a new e-invoicing date.
3. Big "jhatka" business-tech news (AI, big tech, layoffs, outages, price changes, CEO changes) trending in the last
   48 h that small-business owners care about.
4. Evergreen Zoho Books / CRM how-to problems (late payments, reminders, recurring invoices, approvals, workflows,
   bank feeds, custom fields...) - always available, use when 1-3 give nothing solid.

Fact rules (CLAUDE.md rule 3 - wrong facts are never uploaded):
- Every number, date, name and claim must come from an official primary source (government, the company itself) OR
  two independent reputable outlets. Open the pages (WebFetch) - never write from a search snippet alone.
- News must be from the last 72 h (Shorts) / still current (long video). Say the date on screen.
- Real people: only what the sources say, no opinions, no invented quotes, no photos of real people.
- Zoho steps (menu paths, button names) only from Zoho's own help pages AND only screens that exist in
  `assets/screens/index.yaml` (with those exact click targets). If a step cannot be shown on a real screen, show it as a
  board (flow2 / checklist) instead - never invent a Zoho screen.
- If a fact can't be verified, drop it. If the topic falls apart, take the next candidate.

## 2. Two Shorts (~25 min)
- One file per Short: `docs/longform/shorts/sYYYYMMDD-<slug>.json`, `"format": "short"`. Copy the structure of
  `docs/longform/shorts/s20261115-uae-pdf.json` (the first one, approved quality).
- Mix: if there is solid news -> one news "jhatka" Short + one useful how-to; no news -> two how-tos.
- 30-48 s spoken (about 95-150 words), 3-4 scenes, first line = the hook (the surprising fact, no "hi guys"),
  last line = the takeaway / where to learn more. Natural English, short sentences, no hype words ("insane", "shocking").
- `headline`: max ~8 words, one *highlighted* phrase. `kicker`: 2-4 words + date. `source_line`: real sources.
- `title`: <= 90 chars, keyword first (people search it), no clickbait the video doesn't deliver.
- `description`: summary, sources with URLs + "checked <date>", "General information..." line for tax/legal topics,
  the AI-disclosure line ("This video uses an AI-generated presenter, voice and animations..."), and the
  "Independent channel. Not affiliated with or endorsed by Zoho Corporation." line when Zoho is mentioned. Hashtags.
- `tags`: 8-15 real search phrases.
- `caption_fix`: spoken -> written forms for captions (["fifty million dirhams", "AED 50 million"], ["B to B", "B2B"]).
  Write letters to spell out with spaces in the line ("T R N") and map them back in caption_fix.
- Check: `python -m longform.validate <file>`, then render it locally and LOOK at it before pushing:
  `python longform/voice.py F /tmp/v && python -m longform.render F --voice /tmp/v --out /tmp/r --scale 1 &&
   python -m longform.vshort build F /tmp/r /tmp/s.mp4 && python -m longform.qa /tmp/s.mp4 --voice /tmp/r/voice.wav --short`
  then a contact sheet (`ffmpeg -i /tmp/s.mp4 -vf "fps=1/3,scale=270:480,tile=6x2" -frames:v 1 /tmp/c.jpg`) and Read it:
  text cut off, empty frames, overlaps, wrong facts on screen = fix first.
- Push both Shorts in ONE commit -> workflow `shorts-daily` makes, QA-checks and schedules them (next free slot of
  07:30 / 13:30 / 21:30 IST). Result: `docs/longform/shorts-uploaded/<id>.json` or `docs/longform/shorts-failed/<id>.json`.

## 3. One long video (~60 min)
- Topic: the strongest *universal* problem from the research (trending + useful to many small businesses), with real
  Zoho Books screens where possible. id: `<slug>` (lowercase, dashes), different from earlier ids.
- `docs/longform/research/<id>.md`: fact table (fact | value | source URL | official/secondary) + "not verified -> not used".
- `docs/longform/scripts/<id>.json`: same top-level fields as `uae-einvoicing.json` plus `intro_chapter`, `thumb`, `tags`,
  `sources`, `caption_fix`. 7-10 min video = 5.6-10 min spoken (validator), 4-5 chapters, a new scene every 15-40 s,
  at least 3 PODCAST (real screen) scenes when the topic is a Zoho how-to. HOOK first (hook2, 3-5 beats), OUTRO last.
- `thumb`: chip (2-3 words), l1/l2/l3 (1-2 words each, l2 = the yellow keyword), pill (deadline / number / promise),
  pose = one of arms_crossed, open_hands, point_up, point_you, wow.
- Title <= 100 chars, keyword first. Description: summary, `{chapters}` placeholder, sources, disclaimers (as above).
- `python -m longform.validate`, then a quick visual check: voice + `python -m longform.render F --voice V --out R
  --scale 0.5 --plan-only` + `python -m longform.preview R/plan.json R/stills "" 0`, look at a contact sheet of the stills.
- Push the script, the research file and `docs/longform/daily/<id>.json` =
  `{"id": "<id>", "script": "docs/longform/scripts/<id>.json", "publish_at": "<UTC ISO>"}` (default: today 18:30 IST =
  13:00Z if it is before 10:00 IST, else tomorrow 13:00Z). Workflow `longform-daily` (1-2 h): validate -> voice ->
  render 1440p -> QA -> chapters -> thumbnail -> 4K -> upload (scheduled) -> `docs/longform/uploaded/<id>.json` or
  `docs/longform/failed/<id>.json`.

## 4. Watch the runs, retry, never weaken QA
- Poll `gh run list -R GauravSri1020/zoho-shorts` and the result folders every few minutes (Shorts ~15 min, long video
  up to 2 h). On a failure read the log (`gh run view <id> --log-failed`).
- Script problem (validator / QA / text cut off) -> fix the script and push again (same id), or take the next topic
  (new id). At most 2 retries per item.
- Bug in the code -> smallest possible fix on `long-videos`, never relax a QA check, note it in HISTORY.
- A video that is wrong after upload: set it private via a fix request is NOT possible - tell Gaurav at once.

## 5. Report + log (always, also when things failed)
- `docs/longform/topics-used.md`: one line per topic made today (date | type | id | title | video id).
- `docs/HISTORY.md` on `main`: short entry (what was scheduled, failures, fixes).
- SendUserMessage to Gaurav in short Hinglish: the 2 Shorts + the long video (title, YouTube link, publish time IST),
  what failed and why, and the next 5 topic ideas from today's research (so he always has the next searches).

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
