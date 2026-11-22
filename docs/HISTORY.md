# Project history and current status

Is file ko har session ke end pe update karo, taaki agla chat yahin se shuru kare.

## RULE: pehle backup, phir kaam (Gaurav ka standing order)

Gaurav jab bhi kuch bhi change karne bole: SABSE PEHLE backup - `backup-YYYY-MM-DD-<kya-badal-rahe-ho>` branch main se banao (aur agar video ka kaam hai to latest Short ka artifact download karo). Tabhi code chhuo. Kuch bigde to us branch se purana code wapas lo.

## 23 Nov 2026 (01:00-02:40 IST) - Desk screenshots, premium v2, Nvidia trending Short scheduled (bina Flow)

- 12 asli Zoho Desk screenshots (Gaurav ka Desk portal, Zoho ka sample ticket): tickets list / detail / new ticket,
  setup home / channels / automation, Automation Studio (+ new rule), workflow rule, round robin, SLAs, Zia Agents ->
  assets/screens/desk + index.yaml targets. Kuch bhi save / create nahi kiya (har form Cancel).
- Premium v2: real screen pe spotlight (baaki screen dim), glowing ring + "Click: <button>" label, cursor jaldi pahunchta
  hai; bada hook (Anton 118, laal box, number / key word peela, pop); har cut pe whoosh + click sound.
- Desk Short real Desk screens ke saath dobara bana: QA 69.8 (70 chahiye) -> upload nahi; purana ef5oAOBpoxk (QA 71)
  23 Nov 07:30 pe hi. Credit notes QA 67 -> nahi. Dono mein ek hi kami: Flow voice -> narrator voice switch.
- Nvidia: Gaurav ko trending sample pasand. Whiteboard qZqLdG7DKM8 PRIVATE (fix_video "privacy"); sample + purana
  profile-icon corner (longform/corner.py, base clip loop, koi Flow credit nahi) -> IprP0PpvvK0, 23 Nov 13:30 IST
  (longform-upload, upscale false). GALTI: maine Flow pe Nvidia lip-sync clip bana diya (20 credits) - Gaurav ne mana
  kiya tha "Nvidia pe Flow credit mat lagao". Clip flow-clips/flow/2026-11-23 mein save. RULE: Nvidia / news = 0 Flow
  credits; jo Gaurav kahe bas wahi.
- Anthropic IPO spec delete (stale). Flow credits: 80 (reset 2 Dec).
- Open: (1) voice switch ka ilaaj (narrator ko Flow voice ke kareeb laana) - QA isi pe 70 se neeche; (2) research +
  agents tight karna (CRM, Bigin, Sign, WorkDrive, Cliq, Arattai, Creator, Catalyst, Desk; Middle East + baaki desh;
  Zoho / Sridhar Vembu stories) + top Shorts channels ki style study -> writer / editor / QA ke liye guide.

## 23 Nov 2026 raat (00:10-02:30 IST) - PREMIUM Shorts: stuck screen khatam, QA freeze check, 3 Shorts dobara

- Gaurav: "beech mein gandi stuck screen; QA tight kar; face hate to cartoon / whiteboard ya screenshots pe screen-share;
  premium; jo Shorts maine hataye (Desk, UAE) sahi kar; Flow ke unused clips / scripts use kar; Desk ke screenshots".
- Channel audit (naya read-only workflow channel-audit.yml): best = Nvidia all-face Flow news (917 / 300 / 234 views);
  Gaurav ne Na0tD4VPzjc, ck97mHXJSfc, _PWbItoyYAA (+ purane faceless) delete kiye.
- autopilot/premium.py (niches/zoho.yaml flow.premium_middle: true): face ke beech wale shots frame-by-frame, hamesha
  move: REAL = asli screenshot device frame mein, poori screen -> camera click target pe push-in, cursor, ripple, ring,
  menu chips; BOARD = whiteboard: title, menu chips + arrows, icon stroke-by-stroke, tick. Presenter photo card, nakli
  app pages aur cover intro premium mein nahi. editor.frozen_spans: captions ke upar 1.6 s tak picture na hile = FAIL
  (purane Desk / UAE builds 4-4 baar fail, premium pass). composer self-check bhi.
- Results: Desk ef5oAOBpoxk QA 71 (23 Nov 07:30), UAE G_7wRHk9WJo QA 91 (24 Nov 07:30), Campaigns WhatsApp
  r2Y9_r_-Cic QA 93 (24 Nov 21:30). Credit notes QA 64 -> nahi gaya (narrator voice switch + steps 3-4 bina screen).
- Nvidia whiteboard qZqLdG7DKM8 23 Nov 13:30 (wahi). Trending sample (longform/trend) sirf Gaurav ke liye.
- SEEKH: QA ka sabse bada minus = Flow voice -> narrator voice switch. Ilaaj: STEP lines ke liye bhi Flow clips (sirf
  unki AUDIO premium picture ke neeche) - zyada credits (abhi ~50, reset 2 Dec).
- Open: Chrome side panel chahiye: Zoho Desk screenshots, Flow projects ke purane unused clips. docs/UNUSED_FLOW.md.

## 22 Nov 2026 raat (19:20-20:30 IST) - 2 Flow Shorts bane + scheduled, look lock, issues band

- Gaurav: "Flow kholke clips bana, trending news pe 2 Shorts, schedule; teeno clips mein same baal/daadhi/chashma/kapde
  (sirf camera angle alag), agle Short mein naya look, bald kabhi nahi; saare issues close".
- Look lock: hair list se crew cut / fade hataye (Veo ganja bana deta tha), BODY = "full thick hair, never bald, identical
  in every clip, several cameras"; har clip ka apna camera angle (front / left 3/4 / right 3/4). Walk-in-from-side gesture
  hataya (UAE HOOK mein wo frame se bahar reh gaya -> dobara banaya).
- Saare 13 open issues close kiye. DHYAN: issue band = engine job ko "done" maan leta hai -> 1134-2 dobara khola (issue None).
- Gemini quota khatam (429) -> engine ka 2nd script fail. 0930-4 skip (Flow+Claude steps verify nahi). UAE e-invoicing Short
  haath se likha Zoho ke apne ASP guide se (Settings > Taxes & Compliance > E-Invoicing > Setup Now; EmaraTax pe
  "Zoho Software Trading LLC"; Verify & Complete Setup -> ACTIVE; 1 Jan 2027 mandatory AED 50M+).
- Bugs fixed: benchmark ko Gemini list mein JSON de to crash (QA 0) -> list ka pehla object; YouTube "invalid description"
  ('>' in description) -> google_apis.upload har title/description se < > hatata hai.
- Flow project "Nov 22 - 19:27" (main account), 7 clips, 90 -> ~50 credits bache (reset 2 Dec).
- SCHEDULED: Na0tD4VPzjc Zoho Desk Automation Studio (QA 95) 23 Nov 07:30 IST; ck97mHXJSfc UAE e-invoicing Zoho Books
  (QA 93) 23 Nov 21:30 IST. (22 Nov 21:30 wala pehle se scheduled tha.)
- Open: Desk ke steps presenter card pe hain (Desk ke asli screenshots nahi) - Gaurav Desk khole to screenshots le sakte hain.
  Nvidia-style whiteboard/cartoon Shorts (bina Flow) - plan baaki. Brain token (claude setup-token) Gaurav ko karna hai.

## 22 Nov 2026 shaam (17:45 IST) - Zoho Shorts KABHI faceless nahi, long-video brain 20 Nov subah pe wapas

Gaurav: "Zoho Shorts faceless kabhi nahi the: Flow clip -> recorded screens / screenshots -> Flow clip (3 Flow clips),
research agent (Middle East trending Zoho), roz 2 Shorts (fail ho to aur banao); long videos ka code parson se pehle
wala; Nvidia jaisi trending news pe Shorts + long videos bhi". Backup: `backup-2026-11-22-main-before-no-faceless-revert`,
`backup-2026-11-22-long-videos-before-revert`.
- Check: 20-22 Nov mein code sirf 2 jagah badla tha: main autopilot.yml (cron wapas) + long-videos DAILY.md (8 lines).
  longform/ ka code (render, upload, news_short, script-writer) poora hai - wo branch long-videos pe hai, main pe nahi.
- main: `flow.never_faceless: true` -> fallback ab faceless NAHI banata; 30 h tak clips na aaye to job `skip_no_clips`
  (agle din 2 naye Shorts ban sakein). FACE=no Zoho pe ignore. Scout +4 extra angles (QA fail ho to aur try).
  Format wahi: HOOK + PROBLEM Flow clips -> STEP lines asli screens -> RESULT Flow clip.
- long-videos: DAILY.md = dbb41fe (20 Nov subah) + 22 Nov block (Zoho Shorts = main engine, 1 Nvidia-style news Short/day,
  long videos = Zoho + bade trending news jaise Nvidia).
- Waiting abhi: 20261122-0930-4 (Zoho Desk + Claude summary, steps Flow/Claude wale - facts check karne baaki),
  20261122-1134-2 (Zoho Desk turns 10, Automation Studio). Dono ko Flow clips chahiye (Gaurav ka Chrome + Claude).
- ASLI rukawat (code nahi): (1) Flow clips sirf Gaurav ke Chrome mein ban sakte hain - scheduled task cloud-only chalta
  hai -> desktop app mein "Require this computer" on karo. (2) brain ka CLAUDE_CODE_OAUTH_TOKEN fail (is_error) ->
  `claude setup-token` dobara + secret update, tab roz long video khud.

## 20/21 Nov 2026 raat (23:00-01:30 IST) - Shorts wapas PURANE engine pe, long video haath se

Gaurav: "pehle wala kaam hi karna hai - Shorts jaise pehle bante the (engine, Flow ki 1-3 clips, daily schedule),
Flow kam; long video daily; niche pehla wala (Zoho); billing nahi chahiye, free hona chahiye; Flow wali video
schedule se pehle dikhana". Backup: `backup-2026-11-20-main-before-engine-restore`,
`backup-2026-11-20-long-videos-before-engine-restore`.

- Wajah ab bhi wahi: 18 Nov se har Actions run "not started ... spending limit" (20 Nov 13:36 UTC tak check kiya).
  Billing page: GitHub Free, $0 bill, KOI card / payment method nahi - cancel karne ko kuch nahi. $12 included
  compute (2,000 min) khatam, reset ~1 Dec ("11 days"). zoho-shorts $9.68, leadengine-v4 $4.09 (wo bhi minutes khata hai).
  Nov mein: Shorts engine ~1,280 min, longform-daily ~60 min/video. Free 2,000 min mein Shorts engine + roz long video
  NAHI samate. Free raasta: repo PUBLIC (Actions unlimited free) - Gaurav ka faisla baaki.
- Claude ne pehle long-video style ka "hybrid" Short banaya (Flow start + end, beech mein vshort frame) - Gaurav ne
  REJECT kiya: "Shorts bilkul pehle jaise chahiye (channel pe dekho), banner / long-video frame nahi; wo style sirf
  long videos ke liye". Code hata diya (commit nahi hua).
- RESTORE: autopilot.yml cron wapas (07:17 + 08:43 IST daily, comments har 3 h) = fd82ead ka revert. Engine code same.
- 2 Shorts main engine ke jobs mein (haath se, issue null): 20261121-0100-1 Zoho Books credit notes (books/creditnote_new
  real screen), 20261121-0100-2 Zoho Campaigns WhatsApp (screens nahi -> cards). Flow clips sirf HOOK + RESULT (2 each,
  main account project "Nov 20 - 23:14", 80 credits; copy branch flow-clips flow/2026-11-21/). Assemble tab hoga jab
  Actions chalega. DHYAN: cn2 clip mein kalai pe steel kada (rule ke khilaaf), zc1 mein baal bahut chhote (look match
  nahi) - Gaurav ne dekh ke abhi kuch nahi bola.
- Flow galti: menu ke coordinate click se ek clip "Move to trash" ho gaya -> turant Undo (sab 4 clips safe). Aage se
  Flow menu sirf find/ref se click karo, coordinate se nahi.
- long-videos DAILY.md: "Shorts = main engine only, brain = long videos only" (20 Nov wale Flow-spec Shorts rule ke upar).
- Gaurav ne repo PUBLIC kiya (00:40 IST, password khud daala) -> Actions ab free + unlimited, sab workflows chal rahe.
- Long video zoho-books-automation (before-after-demo, 7:00, recurring invoices + reminders + workflow rules, real books
  screens), local render 1080p -> longform-previews -> longform-upload (4K) -> SCHEDULED https://youtube.com/watch?v=EhSLe1zlEzI
  public 21 Nov 18:30 IST, thumbnail set (channel ab verified).
- Shorts: run 44797509836 ne pehle 3 PURANE waiting jobs faceless bana ke schedule kar diye (0859-3 Analytics,
  0921-2 Hotelogix, 0940-4 Zoho Desk = duplicate topics, unverified steps) -> YhuHrqtXsZU, XLhGo9WLVTk, 2KmrL9GwJ2E
  Gaurav ke OK se PRIVATE (delete nahi), slots state se free. Phir credit notes pe Gemini TTS 429 + edge fail mein
  70 min atka -> 90 min timeout cancel. SEEKH: assemble chalane se pehle purane waiting jobs check / skip karo; TTS
  ka per-minute wait loop timeout tak atak sakta hai.
- Run 44811824894: Campaigns Short mein engine ne nakli "Zoho Books" list screen bana di (zoho_screens 35, QA ne
  pakda). Fix: jis step ki asli screen nahi, uska screen = presenter card. Run 44813147677: Campaigns QA 90 ->
  SCHEDULED https://youtube.com/shorts/_PWbItoyYAA 21 Nov 07:30 IST. Credit notes QA 66 (card photo ke kapde +
  edge voice) -> Gaurav: SKIP.
- Open: (1) brain ke liye secret CLAUDE_CODE_OAUTH_TOKEN abhi bhi nahi (issue #177) -> roz ka long video tabhi
  automatic; Gaurav: laptop pe `claude setup-token` -> Settings > Secrets > Actions. (2) cn2 kada / zc1 baal - Shorts dekh
  ke Gaurav decide kare (retake = 20 credits each). (3) leadengine-v4 private hai, wo apne minutes khata hai.

## 20 Nov 2026 raat (00:00-01:00 IST) - Actions minutes khatam, Flow Shorts haath se, script-writer agent

Gaurav: "Flow se videos schedule nahi ho rahe; daily check karo; long video ke liye script-writer agent (har baar
alag structure); Shorts sirf Flow se; roz ek trending news Short; channel analysis; monetization kab; bina approval".
Backup: `backup-2026-11-20-main-before-flow-scriptwriter`, `backup-2026-11-20-long-videos-before-flow-scriptwriter`.

- ASLI WAJAH sab band: 18 Nov ~13:00 IST se HAR GitHub Actions run "The job was not started because recent account
  payments have failed or your spending limit needs to be increased" (GitHub Free = 2,000 min/month, Nov ka ~$14
  khatam; reset "in 12 days" = ~1 Dec). Brain, keeper, shorts-daily, longform-daily, Gemini robot - kuch nahi chala.
  Fix (sirf Gaurav): github.com/settings/billing -> payment method + Actions budget (~$10-20/month) YA 1 Dec tak wait.
- 18-19 Nov ke 6 cartoon Shorts YouTube pe "removed by the uploader" (Gaurav ne delete kiye) -> Shorts ab sirf Flow avatar.
- Flow (main account, project "Nov 20 - 00:08"): 12 clips (240 credits). nv2 (tilak + bead bracelet) aur uae5 (bindi)
  reject; uae5 retake OK; nv2 retake pe Google ka "We noticed some unusual activity" -> dobara try NAHI kiya.
  Clips -> branch flow-clips (flow/2026-11-20/), build `longform.news_short`, upload YouTube Studio browser se
  (Studio COOP: Studio se GitHub popup kholo, popup -> window.opener.postMessage).
  SCHEDULED: fjOlng6WKXY "Nvidia's First Quarter Without Its Founder: $115.8B Revenue" 20 Nov 07:30 IST;
  00hrSpDNju0 "UAE E-Invoicing Starts 1 January 2027: 42 Days Left" 20 Nov 13:30 IST.
- Code (long-videos): `.claude/agents/script-writer.md` (subagent), `docs/longform/STRUCTURES.md` (12 structures),
  `structures-used.md` + validator: long script needs "structure", last 4 se alag. `CHANNEL_INSIGHTS.md` (analysis),
  `flow-specs/` (Flow Short format), DAILY.md "20 Nov changes" (Flow-only Shorts, 1 trending news Short/day,
  sources: LinkedIn News, Reddit, HN, Techmeme, Google Trends...). Cartoon queue item -> queue/shorts-parked.
  main: daily-robot brain allowedTools + Task; autopilot.yml Gemini daily scripts OFF, comments 2x/day (minutes bachao).
- Scheduled task "Flow Shorts daily (GSX Automation)" 10:47 IST roz (2 Flow Shorts + Studio schedule). DHYAN: abhi
  cloud-only bana hai - Chrome ke liye Gaurav Claude desktop app mein task kholke "Require this computer" on kare.
- Channel (lifetime): 3,048 views, 7.2 h, 13 subs; search 60 %, Shorts feed 29.5 %; best = Nvidia news avatar Shorts.

Open: (1) Gaurav: billing / budget. (2) "Require this computer" on the scheduled task. (3) Long video: brain chalega
jab minutes wapas - pehla script-writer wala video. (4) Purane Gemini issues #180 #184 #185 stale (close kar sakte).

## 17 Nov 2026 raat - brain kabhi chala hi nahi (token missing) -> Claude ne haath se queue bhari

Gaurav: "summary do", phir "aage ki videos bana ke aage karo", "ye khaali kyun hai, brain agent chala ki nahi check karo".
Backup: `backup-2026-11-17-before-queue-refill` (main) + `backup-2026-11-17-long-videos-before-queue-refill` (long-videos).

- WAJAH: daily-robot ke saare runs green, lekin brain job 5 s mein skip: secret `CLAUDE_CODE_OAUTH_TOKEN` repo mein hai hi nahi
  (issue #177). Keeper ke paas queue 0 -> 16 Nov 21:30 ke baad YouTube pe kuch scheduled nahi tha. Gemini robot (main)
  ke Shorts: #184 #185 Flow clips ka wait, #180 do baar QA fail (voice change).
- FIX (sirf Gaurav): laptop pe `claude setup-token` -> GitHub Settings > Secrets and variables > Actions >
  `CLAUDE_CODE_OAUTH_TOKEN`. Tab se roz 05:17 IST brain chalega.
- Is chat mein repo session se attach ho gaya (add_repo, git push kaam karta hai; `gh` CLI ka token invalid - Actions
  status browser se dekha).
- 6 Shorts (long-videos, docs/longform/shorts/s20261117-*.json), sab local render + QA pass + contact sheet dekha:
  news Zoho Desk Blended Agents (16 Nov), UAE MD 197/2026 tax-group 24 months; how-to Books Recurring Invoices,
  Purchase Approval, Autoscan, Zoho CRM MCP servers (real screens). shorts-daily #5 -> sab 6 SCHEDULED (IST):
  18 Nov 07:30 Autoscan Ga4U_UkddJ8 · 13:30 UAE tax group 29xVMeskuog · 21:30 Purchase Approval UJ4w_U0ZFDE ·
  19 Nov 07:30 Recurring OR2dny795eU · 13:30 Zoho Desk Blended Agents n0N5Z1lMJxc · 21:30 CRM MCP 8ZF5N60ChjI.
  (Slots file order se mile - alphabetical; news Short ko pehle chahiye to use alag push karo.)
- Long video `zoho-crm-mcp-claude` (7.3 min plan, 5 chapters, 3 PODCAST real CRM screens, thumbnail OK) ->
  docs/longform/daily, publish 18 Nov 13:00Z = 18:30 IST, longform-daily #3.
- BUG FIX longform/vshort.py: Shorts ke captions mein `caption_fix` lagta hi nahi tha (alag process) -> ab build
  mein lagta hai ("FIFTEEN LANGUAGES" -> "15 LANGUAGES"). Purane Shorts ke captions mein spoken form reh gaya hoga.
- Headline rule (Shorts): ~23 characters tak ek line; zyada hua to aakhri shabd akela neeche gir jaata hai.
- DUPLICATE KHATRA: Gemini robot issue #185 (Zoho Desk Blended Agents) = aaj wala news Short; #184 Hotelogix = 12 Nov
  wala Short (4JwXRwzbq28). Clips na aaye to robot faceless bana ke upload try karega - Gaurav decide kare (skip?).
- Research: docs/longform/research/shorts-2026-11-17.md + zoho-crm-mcp-claude.md. Queue (docs/longform/queue) ab bhi
  khaali - agla brain run / agli chat bhare.

## 14 Nov 2026 raat - long video LIVE, 2 Nvidia news Shorts scheduled

- Long video uae-einvoicing v2 YouTube pe: https://youtube.com/watch?v=-JyVV7LA4pA (4K, public 14 Nov 22:00 IST). Thumbnail API 403 = channel phone-verified nahi (youtube.com/verify - Gaurav).
- Gaurav: "Nvidia wale kaand pe 2 videos with my Flow" (channel ka niche Zoho hai, Gaurav ka faisla reach ke liye). Flow main account project "Nov 14 - 19:37" (shaam ko Claude ne banaya; us chat ka context compaction mein gaya, files scratchpad mein mile).
  Facts: Nvidia 8-K 12 Nov 2026 (Huang resigned as President, CEO and board member, effective immediately; Colette Kress interim CEO; internal + external candidates), CNBC 12/13 Nov (affair note to staff, $4T se neeche, -12.75% week), Beinsure (board probe: reports he was targeted by a foreign intelligence operation), FY2026 revenue ~$216B.
  Galtiyan pakdi: "shares fell over 14% at one point" kisi source mein confirm nahi -> wo clip HATAYA; 2 clips mein Veo ne maathe pe lal tilak bana diya (rule ke khilaaf) + ek clip ka huliya alag -> Flow retakes (2113778, 2220291) se Kress video dobara banaya.
  Final (all-face, captions + lower thirds + header + sources line, quiet music): vMv3A-V--Zg "Jensen Huang Resigns: What Is Actually Confirmed" public 15 Nov 12:30 IST; YshGq1w0Ee4 "Who Is Colette Kress? Nvidia's New Interim CEO" public 15 Nov 17:30 IST.
  Upload: branch long-videos workflow longform-upload (push trigger docs/longform/upload-requests/<id>.json, naya "upscale": false = vertical Shorts as-is); videos branch longform-previews/previews/. Result files docs/longform/uploaded/<id>.json.
- Flow project mein galti se 3 khaali "Untitled collection" ban gaye (download menu ke clicks) - Gaurav delete kar de.
- Main pe 2 manual Nvidia jobs bane the, phir hata diye (warna daily run unhe waiting jobs gin ke ruk jaata).
- SEEKH: clips ke prompt mein "no tilak" ke bawajood Veo kabhi tilak bana deta hai -> har clip ka frame dekhna zaroori; aur jo line source mein na mile, wo clip use nahi.

## 14 Nov 2026 shaam - long video v2 + upload, Shorts 3x fail (no usable news)

Gaurav ka review (sample "bahut achha"): thoda slow -> ~1.25-1.35x; Zoho Books screens zyada; kone ka chehra bahut chhota (profile icon jaisa), mic wali photo nahi, 1-2 s bolta hua clip loop; voice yahi free wali par thodi bhaari (apni awaaz NAHI dega); podcast setup clip NAHI; interest loose na ho; research tight; 4K taaki YouTube pe pixel na fate; thumbnail references jaisa (CA Kunal Kumar / Business Solution style). Doosre channels ke tutorials se screen record karke crop karne ko kaha - Claude ne MANA kiya (copyright + reused-content = monetization band).
- Branch long-videos (backup-2026-11-14-before-longform-v2): voice am_onyx (Kokoro, median F0 86 Hz) speed 1.1 + gaps tight = ~194 wpm (1.25 pe 213 wpm aaya = fast-forward, isliye 1.1); video 7:36 -> 5:54. longform/corner.py: assets/base_clips/01.mp4 (Gaurav bolta hua) face crop ping-pong loop, 150 px gol + white ring, CHAPTER/OUTRO chhod ke har scene mein (ffmpeg overlay). PODCAST: photo + mic panel hataya, Zoho screen 1800 px wide. Penalty: AED 50,000 / 12 months cap HATAYA (official MoF page CD 106/2025 + CD 173/2026 summaries mein confirm nahi), "6 months late = AED 30,000" dikhaya. Thumbnail longform/thumb/uae-einvoicing.html.
- Upload: .github/workflows/longform-upload.yml (main pe bhi, sirf workflow_dispatch) + long-videos pe push trigger docs/longform/upload-requests/<id>.json. 1440p master branch longform-previews -> runner pe 4K (lanczos) -> YouTube private, publishAt 14 Nov 22:00 IST, containsSyntheticMedia. Result: docs/longform/uploaded/<id>.json (agle runs se). Thumbnail sirf tab lagega jab channel phone-verified ho (youtube.com/verify - Gaurav).
- Zoho Books (India org Helios, trial over) se 5 nayi real screens: customers_list, item_new, invoice_new, recurring_invoices, creditnote_new (trial banner / extension icon / cursor mask kiye) -> assets/screens/books + index.yaml (main + long-videos). UAE e-invoicing screens ke liye UAE demo org chahiye.
- Shorts: 14 Nov ka 07:17 run fail (Gemini 429 + script QA reject); #269, #270 (Claude ne Run workflow count 2) bhi fail: aaj ki Zoho news mein koi feature/how-to nahi (Microsoft outage comment, Army MoU, sponsored Payroll article) + Gemini 503/504. Koi Short nahi bana. Gaurav se poocha: haath se 2 evergreen how-to Shorts ya skip.

Open: (1) long video upload result check (YouTube Studio / docs/longform/uploaded). (2) Gaurav: youtube.com/verify. (3) Shorts: Gaurav ka jawab; robot mein evergreen fallback jab trending news khaali ho (abhi evergreen_fallback false). (4) UAE demo org -> asli e-invoicing screens. (5) Agla long video: ZATCA Phase 2 (calendar).

## 13 Nov 2026 shaam - aaj ki pehli chat delete (kuch save nahi hua), #167 #168 scripts fix, long-video plan branch

Gaurav: "aaj ki deleted history check kar, kahin save hai to uske hisaab se kaam kar; videos dekh ke schedule kar; long video ke liye calendar branch bana rahe the". Backup: backup-2026-11-13-before-fix-167-168.

- Aaj ki pehli chat ka KUCH bhi GitHub pe nahi tha: 13 Nov ke sirf shorts-bot state commits, koi docs/sessions file nahi, koi calendar / long-video branch nahi, Flow mein 13 Nov ka koi project nahi. SEEKH: CLAUDE.md ka END OF CHAT rule (backup + docs/sessions handoff) har lambi chat ke beech mein bhi chalao, sirf end pe nahi.
- Morning run ne 2 jobs banaye (waiting_for_clips): 20261113-0850-1 (#167, Yettel Hungary x Zoho CRM) aur 20261113-0852-2 (#168, SMEDAN x Zoho Books).
- #167 fix: news asli (TheFastMode 10 Nov: Yettel = Zoho ka Hungary partner, CRM / Zoho One, consultancy + Hungarian support) par script "free bundled Zoho access" bol rahi thi (galat) + "in 5 Minutes" + Webforms path "Developer Space" (asli: Setup > Channels > Webforms, button New Form - real screenshot crm/webforms). Naya title "Auto-Capture and Route Website Leads in Zoho CRM"; teeno clip lines + prompts naye.
- #168 fix: SMEDAN x Zoho programme 28 Aug 2026 ka hai (legit.ng / Guardian NG), 9 Nov wala article sirf "call for applications" -> hook se "just launched" hataya: "SMEDAN is offering Zoho credits to 25,000 Nigerian MSMEs...". Screens: books/recurring_invoices real screenshot hai hi nahi -> books/invoices_list (New Recurring Invoice); Reminders -> books/payment_reminders (Reminder - 1 toggle); Online Payments step se "instant customer payouts" + "40%" hataya. Sirf HOOK clip ka text badla.
- Flow (main account, project "Nov 13 - 19:52"): pehla clip FAILED - "We noticed some unusual activity. Note that browser extensions that modify the page may cause issues." = Google ka anti-automation check. Claude ne dobara / ruk-ruk ke try NAHI kiya (bot-detection se bachna mana hai). Clips Gaurav khud banaye (6 prompts chat mein diye) aur issue ke upload link se daale. Agar clips nahi aaye to kal subah ka run (20 h baad) fallback se FACELESS bana dega.
- Long videos: branch long-video-calendar, docs/LONG_VIDEO_PLAN.md (DRAFT): weekly deep-dive tutorial 8-12 min 16:9, Shanivaar 21:30 IST, pehle 4 topics (UAE e-invoicing 21 Nov, ZATCA 28 Nov, Books payments 5 Dec, CRM leads 12 Dec). Format / frequency Gaurav ne abhi confirm NAHI kiya. Code kuch nahi bana.
- GitHub ka kaam is chat mein browser se hua (session ko repo attach nahi ho paya).

UPDATE (20:15-20:55): Gaurav ne pehle 2 clips khud banaye, phir bola "bana aage" -> Claude ne baaki 4 clips banaye (dobara block nahi aaya). Flow project "Nov 13 - 19:52". Clips -> GitHub: Download -> 720p pe URL.createObjectURL wrap (blob pakdo) + a[download] click block (Gaurav ke computer pe kuch save nahi) -> button -> window.open(upload page) -> postMessage -> DataTransfer -> Commit. Galti se Flow mein ek khaali "Untitled collection" ban gaya (Gaurav delete kar de).
- RESULT: #167 -> https://youtube.com/shorts/RluxaYG5-1A (15 Nov 07:30 IST, run 43447652944); #168 -> https://youtube.com/shorts/YD8raYh68IQ (15 Nov 21:30 IST, run 43447859165). Dono issues close.

Open / agla: (1) 16 Nov ke slots kal subah ka run bharega. (2) Long-video format + din confirm -> phir code (writer / composer 16:9 / workflow task long).

## 12 Nov 2026 raat - UAE e-invoicing series (3 Shorts, haath se jobs) + channel audit

Gaurav: "kal ke liye news dhoondh (US / Middle East), jo keywords search hote hain wahi pakdo, monetize karna hai". Backup: backup-2026-11-12-before-manual-einvoicing-jobs.

- Channel audit (Studio, 28 din): 1,559 views, 3.1 h watch, 74% YouTube SEARCH, 17.6% Shorts feed (39% viewed). Top: UAE E-Invoicing setup (172), Payment Reminders (105), ZATCA Phase 2 (103) = Gulf compliance how-to jeet raha hai. Monetization: abhi 1K subs + 4K h ya 10M Shorts views/90d; 1 Feb 2027 se naye applicants 8K h ya 20M.
- Robot mein topic input nahi -> Claude ne 3 job.json haath se banaye (0904-2 jaisa schema, issue null): 20261112-2045-1 (Jan 1 2027 go-live + Zoho = MoF ASP + Books setup), -2 (AED 50M se kam: ASP 31 Mar 2027, live 1 Jul 2027), -3 (penalties AED 5,000/month, AED 100/invoice). Facts: Zoho TechBizz 28 Oct 2026, Zoho blog, Zoho Books UAE setup article.
- Flow main account project "Nov 12 - 19:42": 9 clips (3 looks). Clips -> GitHub: editor ka Download -> 720p fetch wrap + anchor click block (kuch save nahi hota), clips outfit ke rang / contact sheet se job mein baante.
- BUG mila: YouTube description mein "<" ya ">" = 400 "invalid video description" -> upload fail, job qa_failed. Fix: description mein "›". DHYAN: state save (-X theirs) ne pehla fix overwrite kar diya tha -> dobara lagaya + status waiting_for_clips + Run workflow task assemble.
- Scheduled: qJyJzgDmXr8 (SME deadline, 13 Nov 21:30 IST), EWP-iKwLy60 (penalties, 14 Nov), aHYXCihA-UM (Jan 1 setup, 14 Nov). QA 93 / 92 / 91.6. Screen voice = edge (Gemini TTS quota khatam).
- TODO code: writer/build_description mein < > hatao; workflow input "topic" (Claude ka haath ka job band ho); long-video branch (Gaurav strategy chunega).

## 12 Nov 2026 shaam - #159 script theek karke upload, #160 skip (fake/galat news)

Gaurav: "Flow se videos bana ke sab YouTube pe upload karo; fake news nahi daalni - theek ho sake to theek karo, warna skip". Backup: backup-2026-11-12-before-fix-159-skip-160.

- #160 (20261112-0917-4, Zoho Analytics): story = NewsBytes "Zoho Analytics ~20% annual growth target" = revenue news, koi naya feature nahi; hook ise "launch" bata raha tha. Analytics AI agents Short 11 Nov ko already gaya. -> status skip (+ skip_reason), issue close. Koi clip nahi bana.
- #159 (20261112-0904-2, Optiven): news asli (TV47 11 Nov: Optiven ne Zoho One - Mail/WorkDrive/Cliq/Desk/Forms/Campaigns/Creator - liya, Head of ICT: software cost 40% kam) par CRM/Books article mein nahi. Script mein galat: "today", "up to 40%" sabke liye promise, "under three minutes", "Closed Won pe auto draft invoice" (native nahi). Claude ne job.json haath se theek kiya: hook "Optiven cut its software costs forty percent by moving its teams onto one Zoho stack", steps Zoho Books help doc se (Settings > Integrations & Marketplace > Zoho Apps > Zoho CRM; customers + items sync; CRM deal se estimates/invoices), RESULT bina number. Title "Stop Paying Twice: Connect Zoho CRM and Zoho Books".
- Flow main account (gauravsri069), project "Nov 12 - 19:42", Veo 3.1 Fast x3 = 60 credits. Naya Flow UI: prompt box + -> "Me" (Avatar) -> Add to prompt; settings chip Video 720p 8s 9:16 x1. Clip URL: editor kholne pe performance entries mein flow-content.google/video/<id> (signed) -> fetch blob -> button -> window.open(upload page) -> postMessage -> DataTransfer -> Commit.
- Run 43236091873 -> https://youtube.com/shorts/FJdJEHMpdQw, public 13 Nov 07:30 IST.
- Seekh: scout ab bhi revenue/growth news utha raha hai aur writer case-study ka number sabke liye promise bana deta hai. Fix (code mein abhi NAHI kiya): QA rule - case study number sirf us company ke naam se, "today" sirf <24h news pe, revenue/growth-target news = skip.
- Open: 13 Nov 21:30 slot khaali (#160 skip). Agla: replacement Short (Run workflow daily count 1) ya kal ka 07:17 run.

## 11-12 Nov 2026 raat - Books Short mein Flow screens (galti) -> asli screenshots; CRM Short

Gaurav: "Zoho Books ke video mein Zoho Flow ki screen laga ke QA pass kar diya; mere diye screenshots use karo".
Backup: `backup-2026-11-11-before-real-screens-guard`.
- Galti: writer rule (mera, 10 Nov) "naye feature ke liye flow chain" -> har Short mein Zoho Flow logo wali screens;
  QA product check nahi karta tha.
- Fix: `composer._product_screen` (doosre app / Flow chain wali screen -> Short ke product ka best-match ASLI
  screenshot assets/screens, warna usi product ka page); writer: sirf Short ke product ki screens, real pehle, Flow
  chain sirf Zoho Flow Short mein; script QA + video QA: wrong-product screen = blocker (zoho_screens < 40).
- `job.replaces`: rebuild upload se pehle purani video PRIVATE (delete nahi) + uska slot free.
- Hotelogix Short dobara (Books invoices list / integrations / GST settings real): QA 94 ->
  https://youtube.com/shorts/4JwXRwzbq28, 12 Nov 07:30 IST; purana IKAd19yW0lE private.
- Naya: job 20261111-1800-1 "Zoho CRM Now Sets Itself Up From One Sentence" (official Zoho post: 5 native
  customization agents, Setup > Zia > Models > Zoho Hosted LLM, "Customize with Agent", "Authorize Agent"), 3 Flow
  clips (main account) -> QA 92 -> https://youtube.com/shorts/louAaBoyLT4, 12 Nov 21:30 IST.
- Credits aaj: 6 clips = 120. 12 Nov ke dono slots bhar gaye; 13 Nov ke scripts 12 Nov 07:17 ka run banayega.
- Agla topic idea: Zoho CRM Cadences WhatsApp follow-ups (official post) - facts abhi padhne baaki.

## 11 Nov 2026 (3) - Hotelogix Short SCHEDULED + avatar voice rule

- Flow (main account, project "Nov 11 - 22:32"): 3 clips #153 -> assemble. QA 65/70: sirf awaaz ka farq (avatar "Me" =
  Gaurav ki Indian English awaaz; screen parts Gemini Achird ya edge en-IN-PrabhatNeural dono ko QA "American / doosra
  aadmi" kehta). Gaurav: "awaaz change hai to rehne de, upload kar" + aage "farq chalega".
- Code: avatar Shorts mein screen voice order edge (en-IN-PrabhatNeural) -> gemini -> piper; QA ko voice ka naam milta
  hai -> awaaz ka farq blocker NAHI (baaki sab strict). Faceless Shorts: Gemini pehle, one-voice rule strict.
- Job 20261111-1633-1 `owner_approved` -> https://youtube.com/shorts/IKAd19yW0lE, public 12 Nov 07:30 IST.
  Credits aaj: 3 clips = 60 (sab isi video mein lage).
- Gaurav naraz: bahut time laga (apt mirror + Gemini overload + QA voice rebuilds). Agla: 12 Nov 07:17 run 2 scripts
  banayega -> Gaurav Flow tab khole -> Claude clips + upload -> schedule; ab awaaz se rebuild nahi hoga.

## 11 Nov 2026 (2) - raat: apt mirror down, Gemini overload, Hotelogix avatar job

- GitHub ke Ubuntu apt mirror ghanton down: ffmpeg + browser install steps ab `continue-on-error` (apt errors log
  mein dikhte hain, update fail ho to bhi install try). Script / Flow prompts bina ffmpeg ke bante hain; video bina
  ffmpeg ke khud fail hoti hai (kuch kharab upload nahi). GitHub release se static ffmpeg wala fix permission check
  ne roka - nahi lagaya.
- Run 43048656552 ~90 min: Gemini 503 high demand + 504 (5 min each) -> har script QA round ~6 min; facts step
  (Google Search grounding) free key pe hamesha 429 -> facts nahi milte -> QA ne bane-banaye CRM fields reject kiye
  (sahi). Cancel kiya. Fix: Gemini timeout 5 -> 2 min. OPEN: facts ke liye grounding ke bina raasta chahiye (article
  text khud fetch karna).
- Scout ab integrations / partnerships / customer stories bhi le sakta hai (pehle 0 angles).
- Claude ne khud: job 20261111-1633-1 "Hotelogix + Zoho Books: Hotel Accounts on Autopilot" (issue #153), facts =
  Hotelogix marketplace ka official Zoho Books page; 3 avatar clips, look naye generator se. Flow clips abhi
  BAAKI - Chrome panel ne jawab nahi diya. Agla step: Flow (main account gauravsri069, ~930 credits) mein #153 ke 3
  prompts -> clips -> upload link -> assemble. Agar clips nahi bane to kal subah ka run ise faceless bana dega.

## 11 Nov 2026 - SUBAH script, din mein Flow avatar (Claude), warna faceless + har Short ka naya HULIYA

Backup: `backup-2026-11-11-before-morning-avatar-looks`.
- 10 Nov ka "0 9" cron 11 Nov ko GitHub ne chalaya hi nahi (11 Nov ke saare runs sirf comments) -> koi faceless Short
  nahi bana. Ab cron `47 1` (07:17 IST) + backup `13 3` (08:43 IST), full hour se door.
- Gaurav ka naya flow: subah research + script + Flow prompts (issue). Default = AVATAR (`flow.faceless: false`).
  Gaurav din mein ek baar Flow tab kholta hai -> Claude clips bana ke upload -> GitHub assemble + schedule.
  Flow credit nahi / clips nahi aaye -> `flow.fallback()`: agle subah ke run mein (20 h) ya Run workflow task
  `fallback`, hours 0 -> wahi script FACELESS (photo cards + screens + Gemini voice) + issue comment. 4 din se purana
  waiting job = stale -> skip. Run workflow face `no` = seedha faceless. 20261025-0920-1 (Oct) -> skip.
- Huliya (`flow.look_parts`): outfit = rang (18) x kapda (14), kabhi repeat nahi (state used_outfits); jagah 36 (outdoor
  flag), sab use hone tak repeat nahi (used_places); beard (5) x hair (6) x chashma (5, sunglasses sirf outdoor),
  pichhle Short se alag (last_grooming). Prompt: "in this whole video he has ... - exactly the same in every shot".
  `flow.body`: face / skin / height / build avatar jaisa (hair + beard ab look se); NO tilak, mala, beads, thread,
  religious cheez, earrings, bracelets - professional.

## 10 Nov 2026 (8) - SAB GITHUB MEIN: roz faceless Shorts + avatar jab chahiye

Gaurav: "mujhe ye git me chahiye, Claude pe kuch nahi rakhna". Flow ka API nahi -> avatar clips GitHub se nahi ban
sakte. Gaurav ka faisla: "Dono: free roz + avatar jab main chahu". Backup: `backup-2026-11-10-before-zoho-faceless`.
- `niches/zoho.yaml`: `flow.faceless: true`, `flow.per_day 2`, `scripts.per_day 2`. Daily run (14:30 IST) = research
  -> facts -> script -> QA -> screens + Gaurav ki photo wale cards + cover + Gemini voice -> video QA -> YouTube
  schedule. Koi Flow credit, koi Claude nahi.
- Avatar Short: Actions -> GSX Automation Shorts -> Run workflow -> task daily, face `yes`, upload `yes` -> issue mein
  Flow prompts -> Gaurav Flow mein clips banaye -> issue ke upload link se daale -> assemble + schedule. (workflow
  input `face` wapas.)
- `screens._presenter_page` (view "presenter"): HOOK / PROBLEM / RESULT bina screen ke = Gaurav ki cut-out photo
  (assets/presenter, pose title ke hash se) + line ka card caption + chip NEW / THE PROBLEM / THE RESULT.
- `writer.news_facts`: Gemini + Google Search grounding se news ke asli facts (feature names, menu path sirf agar
  official doc mein) -> writer + QA dono ko. Writer + QA rule: naye feature ka menu facts mein nahi to settings page
  nahi, flow chain / AI chat screen.
- Duplicate story fix: `state.covered_titles` + `research._story_terms/_same_story` (zoho / generic shabd hata ke,
  plural fold, >=2 common + 50%) -> pichhle 30 Shorts ki story dobara nahi.
- Test runs (upload=no): 42838749565 faceless Short ban gaya (cover, photo cards, QA 94.5) - par menus bane-banaye
  aur topic duplicate tha -> upar wale fix. 42842538728: dedupe OK (2 skip), lekin Gemini daily quota khatam (429)
  -> facts nahi chale, QA ne dono scripts reject kiye (sahi). Facts step pehli baar 11 Nov 14:30 run mein chalega.
- Dhyan: jis din achhi Zoho news nahi, us din Short nahi banta (run "no Short prepared" - jaan-boojh ke). Bahut
  testing se Gemini free quota jaldi khatam hota hai.

## 10 Nov 2026 (7) - 2nd Short + har Short pe COVER + har Short ka naya LOOK

Backups: `backup-2026-11-10-before-apt-retry`, `backup-2026-11-10-before-zoho-cover-looks`.
- Daily run (count 2): 20261110-1149-2 (Zoho Analytics AI agents) facts se dobara likha (Ask Zia ke 6 agents,
  semantic layer, Analytics MCP server, AI observability, prices unchanged); 20261110-1209-4 (Arattai + MapmyIndia,
  consumer news, galat SalesIQ screens, 7 clips) skip + issue #146 close. Flow main account, project "Nov 10 - 17:43",
  3 clips -> QA 95/70 -> https://youtube.com/shorts/JiV57TU0m98, public 11 Nov 21:30 IST (Gemini voice, no backup).
- Workflow: ffmpeg/fonts apt install 2 baar 8 min pe atka -> ab 3 short tries (timeout 150/240 s, Acquire retries).
- COVER (Gaurav: "Shorts ke shuru mein meri photo + problem caption, bas starting mein"): `autopilot/thumbnail.py`
  wapas (Zoho-only cleanup mein hata tha). Zoho Shorts ka pehla ~1 s = cover (Gaurav cut-out + bada caption +
  Short ki apni screen + arrow), phir fade. Rang Zoho product se (`composer._ZOHO_ACCENT`), label = app_label.
  Writer ab `thumb_text` deta hai (3-6 words, *key words*). QA ko cover note Zoho pe bhi. cover.jpg custom thumbnail
  bhi try hota hai (channel verified nahi to sirf log). Fix: cover pe screen sides se kat'ti thi -> full width.
- LOOK (Gaurav: "har video ka look alag" = sirf outfit + jagah): `flow.outfits` (20) x `flow.places` (20) in
  niches/zoho.yaml; `flow.pick_look` = kabhi use na hua combination (state `used_looks`), pichhli video se na same
  outfit na same jagah, kam use hue pehle. Aaj ke 2 looks seed kiye. Test: 30 looks unique.

## 10 Nov 2026 (6) - Gemini screen voice FIX

Backup: branch `backup-2026-11-10-before-tts-fix`.
- Asli wajah: google-genai 3.0.0 (requirements `>=1.0` -> runner latest leta hai) ka default API ab `v1` hai; `v1` mein
  speechConfig field hi nahi -> 400 "Unknown name speechConfig" -> har Short ki screen lines backup voice (edge).
  Quota ki problem nahi thi.
- Fix `tts.py`: TTS client `http_options=HttpOptions(api_version="v1beta")`. Models: 2.5 flash/pro preview (pehle
  wali Achird awaaz) pehle, phir Gemini 3.8 Flash / Flash-Lite TTS + 3.1 Interactions API (`client.interactions
  .create`, style = speech_metadata annotation) fallback. (Interactions pe 3.8 abhi "model not found" deta hai.)
- `python -m autopilot.main ttstest` (Run workflow -> task `ttstest`): Short banaye bina voice check. Run 42805726805:
  OK, Achird 6.4 s via gemini-2.5-flash-preview-tts.
- Scheduled Short q4Fsi7ctYDY (11 Nov 07:30) abhi bhi edge voice wala hai - Gaurav decide kare: rakhe ya rebuild.

## 10 Nov 2026 (5) - pehla Zoho trending Short scheduled (Zoho Campaigns AI agents)

Gaurav: "check karke video bana ke upload kar do, dono Flow accounts mein se jo marzi".
- Job 20261110-1008-2 ki script news ke asli facts se dobara likhi (IT Brief 30 Oct / Techeconomy 5 Nov: Campaigns
  mein MCP se AI agent workflows - build / schedule / analyse, permissions + approval; native WhatsApp campaigns;
  frequency capping email + SMS + WhatsApp; paid plans $4/month). Menu naam news mein nahi -> steps general (AI chat
  + flow screens). 141 words. Issue #142 update (REST API; gh GraphQL is session se blocked).
- Flow: Golu Sri (/u/1) pe sirf 55 credits (reset 13 Nov) -> MAIN account gauravsri069 (1,050 credits) use kiya.
  Project "Nov 10 - 16:16" (flow.google.com/u/0/project/3eae42b3-bb38-434e-9b4e-1075a0e7c30f), Veo 3.1 Fast x3 = 60.
  Avatar "Me": har clip pe dobara; dhyan - naya video list mein upar aata hai aur list khisakti hai.
- Clips -> GitHub bina download: fetch + createObjectURL wrap (blob pakdo) + HTMLAnchorElement.click block (Gaurav
  ke computer pe koi file save nahi) -> button -> window.open(upload page) -> listener -> postMessage -> DataTransfer
  -> Commit (918603a). Text match 1.00 / 1.00 / 0.85.
- Run 42803008520: QA 95/70 -> YouTube https://youtube.com/shorts/q4Fsi7ctYDY, public 11 Nov 07:30 IST, titles
  ar/de/fr/es/hi.
- BUG (open): Gemini TTS 400 INVALID_ARGUMENT "Unknown name speechConfig" (quota nahi!) on
  gemini-2.5-flash/pro-preview-tts -> screen lines backup voice edge (avatar se alag awaaz). Fix: current Gemini TTS
  model / API format check karo (tts.py MODELS + speech_config), google-genai 3.0.0.

## 10 Nov 2026 (4) - pehla Zoho-trending run + QA ko news dikhana

Run 42792655507 (count 2): research ne asli Zoho news pakdi (Vembu AI jobs 5 publishers, Zoho Analytics AI agents
3, Zoho Campaigns WhatsApp + AI agents 3). Gemini bahut 503 / 504 / 429 (quota khatam) -> ~55 min.
4 angles: 3 script QA mein fail (galat Analytics API endpoint, Campaigns ka "Zia" engine nahi, Zoho ka restaurant POS
nahi - QA ne sahi pakda). 1 bana: job 20261110-1008-2 "Automate WhatsApp Marketing with Zoho AI Agents" (issue #142).
- Lekin usme news Zoho CAMPAIGNS ki thi, script mein "Zoho Marketing Automation", shayad bane-banaye menus
  ("AI Agent Assistant -> Enable AI Agent") aur "40% engagement" jo kisi source mein nahi -> status `skip`
  (CLAUDE.md rule 3: galat Zoho steps upload nahi). Gaurav is ke clips na banaye.
- Fix: `writer._news_qa_rules` - trending mode mein QA agent ko news (title + summary) milti hai; reject agar
  product news se alag, koi number / % / price news mein nahi, naye feature ke menu ka naam pakka nahi, ya hook
  mein news nahi. (Pehle QA ko story bheji hi nahi jaati thi.)
- Agla: daily run 14:30 IST (Gemini quota reset ~13:30 IST) naye QA ke saath. Zoho Campaigns news (30 Oct - 5 Nov)
  ab bhi 7 din window mein hai.

## 10 Nov 2026 (3) - sirf ZOHO ki trending news

Gaurav: "zoho ki trending news ko pakadna hai". Pehle run (cancel kiya, kuch commit nahi hua) mein top 8 news
saari ek hi Claude Fable 5.2 launch ki copies thi - Zoho ki ek bhi nahi.
- `sources.news_must_mention: ["zoho"]` - news mein "zoho" na ho to topic nahi. Feeds ab sirf Zoho news: Google
  News "Zoho" (US / IN / AE / GB), Zoho launches / announces, Zia / Zoho MCP / Zoho AI, Zoho CRM / One / Books /
  Desk, partnership / integration / pricing, India (Arattai, Zoho Mail, Vembu, GST, Zoho Payments), Gulf (ZATCA /
  UAE e-invoicing), HN "Zoho", Google Trends IN / US / AE. `news_max_age_hours: 168`.
- `research._cluster`: ek hi story ke kai publishers = EK item, `publishers` = kitne chhaap rahe (asli trend).
  Score = (publishers-1) x3 + min(trend,10) + freshness (24h +4 ... 120h +1).
- Scout HARD RULE ab "TRENDING ZOHO NEWS": launch / feature / integration / pricing / compliance / Zoho viral;
  revenue / funding / awards jaisi news skip jab tak usme user ke kaam ka feature na ho.
- Mock test: Claude news drop, 3 copies -> 1 item (3 publishers, top), 9 din purani drop.

## 10 Nov 2026 (2) - SIRF TRENDING NEWS pe Shorts (research + scout)

Backup: branch `backup-2026-11-10-before-trending-research`.
Gaurav: "mujhe trending news per hi chahiye, niche research aur acchi karo, agent sirf trending chizein uthaye".
- `niches/zoho.yaml -> sources`: `trending_only: true`, `news_max_age_hours: 96`, `evergreen_fallback: false`.
  `feeds` = sirf news (Zoho launches, OpenAI / Anthropic / Gemini launches, AI agents, MCP, Salesforce / HubSpot AI,
  WhatsApp / Meta lead ads, e-invoicing UAE / Saudi / Europe / India, TechCrunch AI, The Verge AI, HN front page,
  Google Trends US / AE / IN / DE). `community_feeds` = reddit / stackoverflow (sirf proof, kabhi topic nahi).
  `trending` pillar weight 10.
- `research.py`: trending mode mein news ka score = (kitne alag sources wahi story chala rahe) x2 + freshness
  (24h +4, 48h +2, 72h +1). Bina date wali news nahi. Google News title se publisher alag. Problem bank band.
  Log mein top 8 news score + age ke saath dikhti hain.
- `writer.py` scout: upar HARD RULE - har angle ek NEWS item pe, hook mein news ka naam, sirf news ke facts;
  community / evergreen / story_index -1 wale angles code mein drop. Script writer ko bhi "TRENDING NEWS (x hours
  old)" source milta hai aur hook news se khulta hai. Fresh news na mile to us din Short nahi banta (run fail
  "no Short prepared") - random topic se behtar.
- Mock test: 6 din purani news drop, publisher parse, community + evergreen angle drop - sab sahi.

## 10 Nov 2026 - SIRF ZOHO NICHE (Claude-wealth niche hata diya)

Backup: branch `backup-2026-11-10-before-zoho-only` (change se pehle ka main - Claude niche wapas chahiye to yahin se).
Gaurav: aage se sirf Zoho wala niche chalega, baaki niches nahi chahiye; sirf Zoho ki videos bane aur upload hon.
- `channel.yaml`: `active_niche: zoho`, niches list mein sirf `zoho`. Koi aur niche (env NICHE) ab error deta hai.
- Hataye: `niches/claude_wealth.yaml`, `research/claude_wealth_bank.yaml`, `autopilot/niche_claude_wealth.py`,
  `autopilot/thumbnail.py` (cover sirf Claude niche ka tha), `state/benchmark_claude_wealth.json`.
- Workflow "Run workflow" se `niche`, `face`, `topic` inputs hataye (sirf Claude niche ke the).
- Claude ke 2 jobs jo clips ka wait kar rahe the (20261027-1000-1, 20261028-1047-1) -> status `skip`. Zaroori tha:
  Zoho ka daily run 2 waiting Shorts pe ruk jaata hai (flow.max_waiting 2), aur ye dono bhi gine ja rahe the.
  Ab sirf Zoho ka 20261025-0920-1 wait kar raha hai.
- Code ke `if not IS_ZOHO` branches waise hi chhode (ab kabhi nahi chalte) - Zoho path ek line bhi nahi badla.
  Test: saare autopilot modules Zoho settings pe import hote hain.
- YouTube pe pehle se scheduled Claude Short (6-nZhetyLJ4, 10 Nov 21:30 IST) repo se nahi rukta - YouTube Studio
  mein private / delete karna hai agar nahi chahiye.
- Zoho niche = roz 1 Short (flow.per_day 1), jisme Gaurav ke Flow clips lagte hain (jaise 27 Oct se pehle).

## 2 Nov 2026 raat - Shorts ka THUMBNAIL / cover (Gaurav ka chehra + title + Claude screen)

Backup: branch `backup-2026-11-02-before-shorts-thumbnail` (change se pehle ka main).
Gaurav: Shorts feed mein jo pehla frame dikhta hai wahi "thumbnail" hai - wo ek plain screen card tha, koi rukta nahi.
Chahiye: title likha ho + meri photo + main Claude screen dikha raha hoon (jaise "WhatsApp automation on real estate").
- Naya `autopilot/thumbnail.py`: 1080x1920 cover - bada uppercase title (key words yellow marker pe), Gaurav ka
  cut-out (neeche, ek side), Short ki apni Claude screen tilted card mein (chat > code > chain > pehli screen),
  yellow arrow, aur "$2,000 PER MONTH" sticker jab title / SELL / MATH card mein price ho. Rang = segment accent.
- Photos: `assets/presenter/` (5 poses: point_up, point_you, wow, open_hands, arms_crossed) - uske apne Flow avatar
  clips se frame nikaal ke rembg (u2net_human_seg) se background hataya, Veo watermark crop. index.yaml = side.
  Nayi pose: transparent PNG + ek line index.yaml mein. Pose title ke hash se rotate hoti hai.
- composer.py (sirf Claude niche, Zoho waisa hi): Short ka pehla ~1 s = cover (halka zoom-in, hook voice neeche chal
  rahi, phir 0.2 s fade) -> feed / grid mein pehla frame hi thumbnail. Length / voice sync same. Cover fail ho to
  Short bina cover ke banta hai (kabhi block nahi).
- Upload ke baad `g.set_thumbnail` cover.jpg ko custom thumbnail bhi lagata hai (best effort; channel phone-verified
  na ho ya Shorts ignore kare to sirf log). cover.jpg artifacts + previews branch mein bhi.
- Writer (Claude niche) ab `thumb_text` deta hai (3-6 words, *key words* stars mein). Purane scripts: title se
  chhota text (":" / "that" pe kaat, max 7 words, "with Claude" hata ke).
- QA prompt: pehla ~1 s cover jaan-boojh ke hai - frozen frame nahi.
- Test (local): 3 purane scripts se covers + ek poora render (24.9 s = voice length, cover 0-1 s, phir Short).
- Pehla asli Short with cover: agla daily run (14:30 IST). Jo Shorts pehle se YouTube pe schedule hain unpe cover nahi.
- 2/3 Nov raat: Gaurav ke kehne pe bacha Short 20261101-1640-6 (E-commerce Inventory Tools) cover ke saath assemble
  (run 41500013914): QA 89/70, scheduled 6 Nov 09:30 PM IST (jIzVVIZkDg8). Custom thumbnail API ne 403 diya
  ("doesn't have permissions to upload and set custom video thumbnails") = channel custom thumbnails ke liye
  verified nahi -> Gaurav youtube.com/verify (phone) kare; tab tak Short ka pehla frame hi cover hai.
- Us cover mein 2 kami dikhi, aage ke liye fix: "E-" / "COMMERCE" hyphen pe toota (ab hyphen wale shabd nahi tootte)
  aur khaali code screen ("// your code here") chuni gayi (ab chat > Claude Code command > code > chain > numbers,
  khaali screen kabhi nahi). Uploaded video mein purana cover hi hai.

## 1 Nov 2026 raat (21:00+) - v4: faceless 2/day + audience segments + YouTube schedule

Gaurav: dono Claude Shorts YouTube pe schedule karo; wealth niche B2B (CEO / business owner) + salaried investor
(IPO, gold/silver Diwali, insurance) + 3-6 lakh wale free tools se kamaayein + sirf phone wale (simple) + developers;
roz 2 videos, poore hafte ka stock; credits na ho to bhi video jaaye (bina chehra); Zoho niche alag file mein rahe.
- Scheduled (owner_approved): video editing 1303-1 -> 1 Nov 9:30 PM IST (XlQM0Y3s8Ls, QA 95 Gemini voice);
  podcast clips 1430-1 -> 2 Nov 7:30 AM (nvndlkV21F8, QA 58, Gaurav approved).
- `niches/claude_wealth.yaml`: `niche.segments` (beginner_free, b2b_ceo, investor_research, developer_side,
  simple_phone, claude_tips) - har ek ka audience, about (safety ke saath), accent, format (money recipe ya apna).
  Rotation `state.rotation.claude_wealth_segment`. `flow.faceless: true` + `flow.per_day 2` + `scripts.per_day 2`.
- Faceless: FACE_BEATS khaali -> koi Flow clip nahi, har line screen + ek hi TTS voice (voice-change problem khatam);
  job status "ready"; daily run hi build + QA + schedule karta hai (workflow daily pe bhi ffmpeg / browser install).
  Run workflow input `face: yes` = chehre wala Short (HOOK clip) jaise pehle.
- Fix: same run mein bane faceless job ko `_still_pending` "already finished" samajhta tha -> upload nahi hota tha.
- Research (Gaurav ke channels): Patrick Dang "laziest way to make money with Claude at night" (AI ad studio,
  ~$2K/month/client, Meta Ad Library), Mark Tilbury "laziest way with AI" 8.4M, Ishan Sharma "start a business with
  Claude Code 2026", Easy AI Coding (websites with Claude Code). 3 recipes bank mein + benchmark references.
- Gaurav ko bataya (policy): investing = sirf "Claude se research", kabhi buy/sell tip nahi; doosron ke podcasts /
  kathas re-upload = copyright + reused content - nahi; original Krishna kahaniyan (public domain) alag channel pe
  behtar. Face clips sirf jab Claude session open ho (Flow Chrome mein chalta hai).
- Batches: daily count 4 (2 QA pass, 2 QA fail -> rebuild) + count 6 queued.
- Batch result (1 Nov raat): 10 Shorts scheduled 1-6 Nov (07:30 + 21:30 IST) - list in state.json slots. QA noisy
  (same video 92 / 63) -> Claude niche `benchmark.publish_floor: 55`: technically clean Shorts schedule even under 70.
- Limits hit: YouTube "exceeded the number of videos they may upload" (~10-11 uploads / day for this channel) -
  1640-6 retries in the next run; Gemini free quota 429 by night -> daily cron moved 10:00 -> 14:30 IST ("0 9 * * *"),
  after the quota reset (~13:30 IST). Pending runs in the "autopilot" group get cancelled when another run queues
  (one pending max) - re-dispatch after the running one finishes.

## 1 Nov 2026 raat - Claude niche v3 "money recipe" (Gaurav ne v2 reject kiya)

Backup: branch `backup-2026-11-01-before-money-format`.
Gaurav ka feedback (v2 video-editing Short): "samajh nahi aaya kya hai / kyun; wealth se related nahi; Claude Project se
koi wealth nahi banta; screens bekaar, Claude jaisi nahi lagti; crop / grey kharab; credits waste". Chahiye: jo video
dekhe woh paise kamaye - 60 s ke andar.
- Script (niche_claude_wealth.py MONEY_SHAPE + _MONEY_RULES): HOOK (face: kaun kitna pay karta hai kis cheez ke liye) ->
  SELL (kya becho, kisko, price range + named source) -> CLIENTS (pehla client kahan + Claude DM likhe) -> STEP 1 (Claude
  asli kaam, exact prompt) -> STEP 2 (delivery chain) -> MATH (example month, source ke low end pe, "not a promise")
  -> RESULT (catch + is hafte kya karo). 110-150 words. Scout: "wealth" = koi paid service / product jo viewer bech sake.
- Screens v3 (screens.py _chat_page_v3 / _money_page, sirf Claude niche): Claude app jaisa cream chat (serif answer,
  beige user bubble, "Reply to Claude..." box), bada bold money card (total green), chain bada; highlight = yellow
  marker (grey dim + red box + cursor hata diye); composer zoom ~1.04 (crop nahi); labels WHAT TO SELL / FIRST CLIENT /
  STEP / THE MONEY / THE CATCH.
- Presenter shot pe dark lower band (composer._lower_band): Veo ne hook clip mein garbled subtitles jala diye the
  ("500s$000 Cladess a morth") - band unhe chhupata hai, captions us par.
- Topic order (Gaurav): video editing -> local business services (healthcare admin, real estate, restaurants) -> free
  GitHub Claude Skills (open_source_skills weight 4) -> trading tools (no tips).
- Job 20261101-1430-1 (issue #94) "Sell Podcast Clips with Claude: $500 a Month per Client": hook / MATH / STEP 1 haath se
  theek kiye (AI ne "$1,500 according to ClipSpeed" aur "< 6 hours" gadha tha). Source: ClipSpeed rate guide 2026
  ($500-$2,000/month). Hook clip main ID se (20 credits; main pe ab 10 bache, reset 2 Nov 3:45 PM). Video 34 s,
  Gaurav ko bheja. QA 60-67 (voice: Gemini TTS quota khatam -> edge voice; "presenter sirf hook mein"). upload=false.
- Rejected v2 job 20261101-1303-1 -> status skip.
- Next: Gemini TTS quota wapas aane par (kal) 20261101-1430-1 dobara assemble (status qa_failed -> rebuild hota hai) ->
  voice match behtar. Gaurav haan bole to owner_approved + upload true.

## 1 Nov 2026 - Claude niche v2 (1 clip + industry screens, 1.5x) + Zoho #66 from existing clip

Backup: branch `backup-2026-11-01-before-zoho-and-claude-clips` (main jaisa tha, v1).

Gaurav ne maanga: ab har Short mein sirf EK Flow clip (tera chehra, max 2), baaki Claude screens + text; pace 1.5x;
zyada professional - alag jagah / background; har industry (video editing, marketing, healthcare, trading,
logistics...) mein Claude se wealth / automation; real news / trending free Claude Skills GitHub repos; kuch fake,
rumour ya illegal nahi. Zoho niche alag hi rahega (settings same).

- Pipeline 28 Oct se ruka tha: 4 Shorts clips ka wait (Zoho #66 #73, Claude #82 #84) -> daily run skip.
- `niches/claude_wealth.yaml` v2: `flow.face_beats: [HOOK]` (1 clip), `speed 1.5` + naya `tts_speed 1.5`
  (screen voice bhi same pace), `max_waiting 4`, 8 outfits; `niche.industries` = 13 fields (id, name, accent
  colour, about + safety, place). Naya pillar `open_source_skills` (trending free Claude Skills / MCP repos on
  GitHub), trending weight 3, skip mein rumours / fake screenshots / illegal; nayi feeds (GitHub skills, industries).
- flow.py: SPEED cap 1.6, TTS_SPEED (Zoho = 1.0, untouched), look = outfit + industry place (Claude niche),
  env TOPIC (workflow input "topic") = us din ka hand-picked topic, industry rotation `state.rotation.claude_wealth_industry`.
- niche_claude_wealth.py: scout ko industry order + topic; script mein sirf HOOK face, PROBLEM / FIX / STEP / RESULT
  sab screens (PROBLEM = numbers / client chat card, RESULT = before/after + catch); mix of screen types.
- composer.py `_layers_v2` (sirf Claude niche): dark navy card, industry colour glow + grid, industry naam upar.
  Zoho card unchanged. Local render test: /tmp frame theek dikha.
- Jobs: #66 #73 #82 #84 ab sirf HOOK clip maangte hain. #66 ke paas hook clip pehle se tha (Golu Sri) -> assemble
  (upload=false, Gaurav pehle dekhe). 
- Naya Short: run "daily" + topic "video editing with Claude" -> job 20261101-1303-1, issue #86 "How Video Editors
  Automate Repurposing Retainers With Claude" (upload=false). Hook clip main ID (gauravsri069, flow.google.com
  bina /u/1) se Veo 3.1 Fast (20 credits), project "Nov 01 - 18:40". Clip GitHub pe: page mein
  performance entries se flow-content /video/ URL fetch -> blob -> button -> window.open(upload page) ->
  postMessage(blob) -> DataTransfer -> Commit (koi download nahi hua).
- Flow UI (1 Nov): naye project mein right side "Agent" panel khulta hai - band karo, prompt box mein "Agent" chip
  off karo, tab settings chip (Video | 9:16 | model | x1) dikhta hai. Default model Omni 1.1 Flash + x2 - Veo 3.1 Fast
  + x1 chuno.
- Analytics (Oct 4-31): 1.4K views, 433 engaged, 12 likes, +12 subs (total 12), 2.8 watch hours; traffic 70.5%
  YouTube search, sirf 17.2% Shorts feed; 52.9% stayed / 47.1% swiped away. Top: UAE e-invoicing (157), ZATCA (91).
  YPP: 1,000 subs + 10M Shorts views / 90 din (1 Feb 2027 se naye applicants: 20M Shorts views ya 8,000 hrs).
- Results: #66 (sirf hook clip) QA 58 - voice change 0:05 (avatar Indian accent -> narrator) -> status "skip" +
  "parked" note (Gaurav run 41309204763 ka artifact dekhe; theek ho to owner_approved). Video-editing Short
  20261101-1303-1: QA 66 -> fixes (Claude niche: TTS style + Flow accent Indian English, backup voice
  en-IN-PrabhatNeural, gentle zoom 1.18 taaki text na kate, music 0.34) -> QA 65 (36 s). Gemini TTS quota aaj khatam
  tha -> screen voice edge. Bacha blocker: avatar voice vs TTS voice (1-clip design mein hamesha switch hota hai).
  Video Gaurav ko chat mein bheja; status qa_failed, upload=false. Haan bole to job.json owner_approved + upload true
  -> assemble.
- Naya: workflow har assemble ke baad Shorts ko branch `previews` pe copy karta hai (newest 6) - artifacts Claude
  session se download nahi hote (blob host 403), previews branch se `git show origin/previews:<job>/short.mp4`.
- Script mein ek number "Up to 50% reported by agency studies" - source naam nahi hai (rule todta hai). Agle scripts
  ke liye QA ko "named source" pe aur strict karna hai.
- Open: Gaurav PDF (exhibitors promote) - link "Missing files" deta hai, chat mein attach karna hai.

## 27 Oct 2026 raat - pehla Claude-wealth Short end-to-end TEST (pass)

- Gaurav: Claude ka koi scheduled task / artifact nahi chahiye; sab GitHub se chale; paid kuch nahi; Flow theek hai. "GSX Flow clips autopilot" task kabhi save hi nahi hua (computer approval nahi) - koi Claude scheduled task active nahi.
- Run #141 (manual daily, niche claude_wealth, upload=no) -> job 20261026-1943-1, issue #78 "Turn Your Weekly Routine into Claude Skills You Can Sell" (bank order 1). Scout ne rotation sahi follow kiya.
- Flow: Golu Sri (/u/1, srig9056) 65 credits; main gauravsri069 50 credits. Project "Oct 27 - 01:16" (flow.google.com/u/1/project/108da973-e1d6-47ba-907e-7c0c7f951eec). 3 clips x Veo 3.1 Fast (20) = 60 credits, 5 bache.
- Flow UI (Oct 2026): New project -> prompt box ka settings chip: Video | Ingredients | 9:16 | model | x1. Models: Omni 1.1 Flash (12 credits / 8s 720p - naya, sasta, abhi test nahi), Veo 3.1 Lite / Fast (20) / Quality. Avatar: prompt box "+" -> asset list -> "Me" (Avatar) -> Add to prompt. Har send ke baad avatar hat jaata hai - har clip pe dobara lagao, aur list mein naye videos upar aate hain: naam dekh ke "Me" chuno (ek baar galti se video lag gaya tha, send se pehle pakda).
- Clips -> GitHub: editor page pe fetch-hook (window.fetch wrap, video blobs), Download -> 720p; Flow page pe button -> window.open(upload page) -> us tab mein message listener + DataTransfer -> Commit to main. Teeno clips ek commit -> run #142 assemble -> QA PASS ("Short ready", upload=no isliye YouTube pe nahi gaya). Video: run 40390928994 artifact.
- Clips ka contact sheet: ek hi look (navy blazer + skyline), koi burned-in subtitle nahi, gestures alag (stop-hand, hands, thumbs up).
- #66 (Zoho) PROBLEM clip mein Veo ne garbled subtitles jala diye the - retake chahiye.
- Open: Gaurav video dekhe (run 40390928994 -> Artifacts). Theek ho to us job ko upload karwana (job.json "upload": true + re-assemble, ya agle Shorts upload=yes). Daily 10:00 run script banata hai; clips abhi bhi browser se (Gaurav ya Claude in Chrome) - koi auto scheduler nahi, Gaurav ke kehne pe.

## 27 Oct 2026 - NICHE SWITCH: Zoho -> "Claude se wealth" (Zoho code waisa hi)

Backup: branch `backup-2026-10-27-zoho-before-claude-wealth` (commit 2ad7606) + repo mein `backups/2026-10-27_ZOHO_BACKUP/` (README + "ZOHO BACKUP" logo + code + settings copy). Git tags proxy block karta hai, isliye tag nahi bana. Short artifacts (runs 24 Oct) is session se download nahi hue (GitHub ka blob storage host blocked) - videos YouTube pe already hain.

- `channel.yaml` ab sirf SWITCH hai: `active_niche: claude_wealth`. Wapas Zoho = `active_niche: zoho` -> Commit. Ek run ke liye: Actions -> Run workflow -> niche.
- `niches/zoho.yaml` = purana channel.yaml, ek line nahi badli. `niches/claude_wealth.yaml` `extends: zoho` (presenter, looks, gestures, schedule, QA limits wahi), apna niche/feeds/pillars/benchmark.
- Code: har jagah `if not IS_ZOHO` switch; naya niche ka dimaag `autopilot/niche_claude_wealth.py`. Test: purane code vs naye code (NICHE=zoho) ke saare prompts, titles, descriptions, screens HTML, QA prompts byte-identical.
- Har job.json mein `"niche"`; purane jobs = zoho. Assemble pehle active niche ke jobs banata hai, phir baaki niche ke jobs child run mein unki apni settings se (#66, #73 Zoho hi rahenge). Claude niche mein sirf apne waiting jobs gine jaate hain (Zoho ke 2 waiting jobs Claude ko nahi rokte).
- Rotation: 4 wealth -> 1 problems (state.json `rotation.claude_wealth`). Pehle 5 bank mein `order` 1-5: Claude Skills bechna, Claude Code se "finish my app" service, local business AI intake automation, Claude Project se social media service, phir problems #1 = YouTube inauthentic-content / AI persona demonetization.
- Research bank: `research/claude_wealth_bank.yaml` (har number ke saath source; trading sirf myth-busting).
- Naya screen "notes" (numbers / checklist card). Claude niche mein Zoho app pages nahi banti.
- Benchmark rubric alag file: `state/benchmark_claude_wealth.json`; workflow ab `state/*.json` commit karta hai.
- Scheduled task "GSX Flow clips autopilot" (roz 11:05 IST, auto approval): Chrome mein Flow /u/1 -> clips -> GitHub upload. ABHI computer se bound NAHI hai -> Claude desktop app mein us task pe "Require this computer" on karna hai, warna cloud mein chalega aur Chrome nahi milega.
- Galti: local dry-run ne asli issue #77 bana diya ("Sell your know-how as Claude Skills") - test hai, Gaurav close kare (Claude ko close karne ki permission nahi mili).
- YouTube rule (support.google.com/youtube/answer/1311392): AI persona se health / legal / financial advice = monetization nahi. Isliye niche "kaise kamate hain" (business + tools) hai, kabhi stock/crypto/trading tip nahi. QA isko block karta hai.

## 24 Oct 2026 (shaam) - #47 + #46 scheduled, clips seedha git push se

Backup: branch `backup-2026-10-24-before-47-clips`.

- Gaurav ne 6 downloaded clips chat mein diye = 3 unique (baaki byte-same duplicates), teeno #47 (20261015-2229-3). Claude ne seedha `git push` se jobs/20261015-2229-3/clips/ mein daale (koi manual upload nahi) -> run #125.
- Run #125: #47 scheduled 25 Oct 09:30 PM IST (8Dqrvvh7n2I), #46 scheduled 25 Oct 07:30 AM IST (zQZbqqgF6IM) - #46 pe clips nahi badle, sirf re-assemble se QA pass (screen part backup voice 'edge', Gemini quota khatam). #53 scheduled 24 Oct 09:30 PM IST (KkEUyae9-RI).
- Flow: Golu Sri = srig9056 = Flow URL `/u/1/` (bina /u/1 kholo to main account khulta hai - Gaurav ko ye pasand nahi, hamesha /u/1). Golu Sri pe ~55 credits, avatar "Me". Ek extra #47 Clip 1 galti se generate hua (20 credits).
- #66 (20261024-0903-1): Golu Sri pe clip 1 + 2 bane (project "Oct 24 - 16:04", flow.google.com/u/1/project/e7b427c3-3b2d-4fba-bb62-6bd562ddb222) aur Flow page se seedha GitHub upload (fetch-wrap + window.open + postMessage + DataTransfer). Open: clip 3 (RESULT, "Cut ticket resolution time in half...", smiles + opens both arms) - Golu Sri pe ~15 credits bache, kal +50 aane pe banao. Screen-part voice change ka asli wajah (tts.py) abhi bhi check nahi kiya.

## 24 Oct 2026 - YouTube token + #53 owner-approved

Backup: branch `backup-2026-10-24-before-owner-approve-override` (change se pehle ka main).

- YT_REFRESH_TOKEN expire / revoke ho gaya tha (runs #119, #120: `invalid_grant`). Gaurav ne OAuth Playground se naya token banake secret update kiya (Google Cloud project `gsx-shorts-511217`, "Web client 1", app already "In production"). Test: run #123 (comments) bina error.
- #53 (20261017-0845-1): clips Flow se bane (2 gauravsri069 pe, 1 srig9056 pe), run #121 -> QA 58/70 (voice change 0:12-0:41, screen part). Gaurav ne video dekh ke bola upload karo.
- Naya: job.json mein `"owner_approved": true` -> sirf us job pe QA block skip (flow.finish). Baaki sab Shorts pe QA utna hi strict. Ye flag tabhi lagao jab Gaurav ne khud video dekh ke haan bola ho.
- Open: #47 (20261015-2229-3) clips nahi bane; #46 (20261015-2228-2) qa_failed, retakes chahiye; #66 (20261024-0903-1) clips ka wait. Screen-part voice change ka asli wajah (tts.py) abhi check nahi kiya.

## 14 Oct 2026 - Flow account switch + presenter variety

Backup: branch `backup-2026-10-14-before-presenter-variety` (change se pehle ka main).

Clips kyun nahi ban rahi thi: robot theek tha (research + script + issue roz ban rahe the). Clips Flow mein haath se / Claude in Chrome se banti hain - kisi ne banayi nahi + purane account (gauravsri069) mein credits khatam (~90 -> ab ~30). Naya Flow account: srig9056 (920 credits, project "Oct 13 - 22:36"). GEMINI_API_KEY badalni ho to: repo Settings -> Secrets and variables -> Actions -> GEMINI_API_KEY -> Update (abhi zaroorat nahi, purani key chal rahi hai).

#17 (20261014-0941-1, Stuck CRM deals): purane account se 3 clips -> run #53 -> scheduled 15 Oct 07:30 IST (A3r_WPRLf_U). Outfit avatar wala grey blazer aaya (look wala nahi) - teeno clips same.

Gaurav ka feedback (presenter): har clip mein same chalna / dekhna; body kabhi patli kabhi theek; location hamesha office; kapde ek jaise. Chahiye: alag gesture + body language har baar, alag jagah (office ke bahar campus/park, street, terrace, lounge), body bilkul reference photos jaisi, kapde smart-casual mix (na Gen-Z, na stiff formal).

Kya badla (sirf prompt text, editor/QA/pipeline code nahi chhua):
- channel.yaml flow.looks: 12 naye smart-casual looks, kai outdoor (corporate campus walkway, city sidewalk, rooftop, cafe terrace, office park courtyard, lounge, lobby).
- channel.yaml flow.body: chehra, skin tone, baal, beard, height, build reference photos jaise - "never slimmer, never heavier" har prompt mein.
- channel.yaml flow.gestures: beat-wise pools (HOOK/PROBLEM/FIX/STEP/RESULT/CTA/ANY). Research: presenter kabhi poora still nahi, walk-in, weight shift, ek dost se baat jaisa tone, ~15% zyada energy.
- flow.py prompt(): har line ke liye pool se gesture (line text se seed, isliye clips mein alag). "walk" wale gesture pe camera = smooth gimbal (warna static). Tone: "confident, friendly business tech explainer, smart and natural, not stiff".

Open / next:
- #15 (20261013-1228-3, Sort Inbound Emails) - naye account ke project mein email/inbox wale clips dikh rahe hain ("Man talking about inbox assistant", "Man explaining email sorting AI") - check karke upload karna hai; agent ne "six video generations" bhi queue kiye the.
- Gestures abhi fixed pool se aate hain. Agla step (Gaurav ne maanga): research agent roz trending Shorts presenters ka body language / hook style dekh ke pool update kare.
- Naye prompts ka pehla test: kal 10 baje wala issue.

## 13 Oct 2026 shaam - voice + black screen fix, editor/QA tight

Backup: branch `backup-2026-10-13-before-voice-blackscreen-fix` (fix se pehle ka pura code). Latest 4 Shorts ke artifacts (runs #39, #41, #42, #43) Gaurav ke browser mein download kiye.

Problem 1 - black screen 3-5 s (YouTube pe gaya): screen lines ke neeche flow.py ek KAALA placeholder video rakhta hai; composer whisper word-timings se decide karta tha kab presenter / kab screen. Sabse sambhav wajah: timing 1-2 s galat -> presenter shot placeholder mein chala gaya = kaala screen. Purana check (blackdetect d=1.0, default pic_th) captions wale kaale frame ko pakad hi nahi paata tha.
Fix: flow.build har part ki EXACT length (clip / TTS line) ka timeline banata hai -> composer.plan_parts() shots wahi se lagata hai (word timings sirf captions ke liye). composer final edit pe black_spans() chalata hai - 0.1 s bhi kaala (captions ke neeche bhi, pic_th 0.85) = build fail, upload nahi. editor.check_media bhi wahi strict check. Veo clip ke start/end ka black fade prep_clip mein kat jaata hai.

Problem 2 - awaaz badalna: tts.py har 429 ko "quota khatam" maan leta tha (asal mein aksar sirf per-MINUTE limit hota hai) aur line-by-line fallback karta tha -> ek hi Short mein lines alag-alag awaaz mein.
Fix: per-minute 429 -> retryDelay wait karke wahi Gemini voice (Achird). Backup voice (edge / Piper) SIRF jab har Gemini TTS model ka DAILY quota khatam ho. tts.speak_all(): Short ki saari screen lines EK hi provider se - kabhi mix nahi. Har line whisper se suni jaati hai (Gemini kabhi style-instruction bol deta hai / shabd kaat deta hai) -> galat ho to dobara. Backup voice laga to issue comment mein likha aata hai.

Editor tight: har part ki loudness same (loudnorm per part) -> clip aur screen voice mein volume jump nahi. Andar 1.2 s+ dead air = note (upload block).
QA tight (benchmark.py): editor checklist - black frames, voice change, same outfit/background, lips, screens, captions, music, ending. Naye criteria "continuity" + "voice". black_frames / voice_changes (jab Gemini voice tha) = blocker. Koi bhi criterion < 55 = blocker. min_score 65 -> 70 (channel.yaml).

Issue #2 (Bill approvals, job 20261011-1326-1) = uploaded_manually (TuYUCh3cP6o) - kuch karna baaki nahi, issue close kar sakte ho. Agla pending: #15 (20261013-1228-3, Sort Inbound Emails) clips ka wait.

## Niche v2: "AI + Zoho automation" (12 Oct 2026, dopahar)

Backup: git branch `backup-2026-10-12-before-ai-niche` (purana code + jobs, sab kuch). Wapas jaana ho to us branch se files le lo.

Naya niche (channel.yaml -> niche): har Short ek real business problem, ideally is hafte ka trending topic, aur fix Zoho ke andar, jahan ho sake AI kaam kare. 5 pillars (weights):
- trending (3): is hafte ki AI / tech / deadline news -> "aaj hi Zoho mein kaise use karo"
- ai_agent (3): Claude / ChatGPT via Zoho MCP, Zia Agent Studio agents, Zoho Flow AI step, Deluge -> AI API
- lead_flow (2): Facebook/Instagram ads (Zoho Social) / WhatsApp / website form / email -> Zoho CRM, AI scoring + routing
- dev_api (2): API endpoint, scope, credits/limits, custom API, webhooks, widgets, Catalyst, Zoho Sign API - exact call dikhao
- problem_fix (1): classic Zoho fixes, AI twist ke saath

Research (autopilot/research.py): naye feeds - AI news (Google News), MCP / AI agent (Hacker News), r/CRM, r/automation, r/smallbusiness, UAE + Europe business news, Google Trends (US, AE, DE). Har item ko "trend" score milta hai (kitne alag sources same baat kar rahe hain) - trending pehle.
Problem bank: `research/problem_bank.yaml` - 27 real problems with verified facts (Zoho MCP setup, Zia Agent Studio, Zoho Social lead ads -> CRM steps, CRM API credits/concurrency, UAE e-invoicing timeline, ...). Gaurav apni Zoho problems yahin add kare (format file mein likha hai). Scout har din bank + feeds dono dekhta hai, koi problem repeat nahi hoti.

Script (writer.py): ab sirf Zoho Books nahi - koi bhi Zoho app + AI chat + API call + code + Flow chain. Global English (Middle East, Europe, US, India). Description mein "API / tool used" block.

Screens (screens.py): har Zoho app ka apna look (CRM, Books, Desk, Creator, Social, Flow, Analytics, Sign, Catalyst, SalesIQ, Inventory) + naye views: AI chat (Claude/ChatGPT + "Zoho connected" + MCP tool), API call (method, URL, headers, body, response), code editor (Deluge / JS, line highlight), Zoho Flow chain. Asli screenshots: `assets/screens/index.yaml` mein add karo -> writer unhe prefer karta hai ("real" key). Abhi library khaali hai - Gaurav Zoho mein login kare, phir Claude screenshots le ke add karega (account banana / password daalna Claude nahi kar sakta).

Global targeting:
- Flow prompt accent: channel.yaml -> flow.accent ("a clear, neutral international accent"); TTS style + backup voice (en-GB-RyanNeural) same.
- Har upload pe title + description Arabic, German, French, Spanish, Hindi mein bhi (YouTube localizations; viewer ki language mein dikhta hai). Fail ho to upload bina translations ke ho jaata hai.
- Publish windows (IST): 17:30-18:30 (UAE 16:00, Europe lunch) aur 21:30-22:30 (UAE 20:00 prime, Europe 18:00).
- Looks: 6 outfits + offices rotate (skyline office, startup office, meeting room, home office, co-working, purana grey blazer).

Safety fixes: assemble ab closed issue wale job ko kabhi dobara build/upload nahi karta (12 Oct ko 1812-5 aur 1816-7 ke folders reh gaye the - duplicate upload ka risk tha; dono "done" mark kiye).

12 Oct ke clips: Flow project mein bane 12 clips GitHub pe upload kiye - 1824-11 (#12), 1823-10 (#11), 1807-3 (#5); 1813-6 (#8) baaki tha jab browser connection toota. Bache hue jobs jinke clips bane hi nahi: 1827-12 RESULT (1), 1809-4 (6), 1821-9 (6), 1828-13 (4) = 17 clips (~340 credits). Ye purane niche ke Shorts hain - banana hai ya band karna, Gaurav decide kare.

## 12-13 Oct raat (Claude akela, Gaurav bahar) - kya hua

- Niche v2 code push (5 commits) + test: run #33 ne 1807-3 (13 Oct 18:09, oSE8KY9KftE) aur 1823-10 (13 Oct 22:01, i5NMCCIRXio) schedule kiye. #34: 1813-6 Creator PDF (13 Oct 17:32, V_2WpXtoCsk), QA 94/65.
- TTS: Gemini free quota 429 + edge-tts 403 (Microsoft ne GitHub runners block kiye) -> 0 Shorts ban rahe the. tts.py ab Gemini -> edge -> Piper (offline, default en_US-ryan-high; badalna ho to channel.yaml flow.piper_voice) - ek baar fail hua provider us run mein dobara try nahi hota. requirements: piper-tts.
- Bug: push-run purana trigger commit checkout karta tha -> state save pe git conflict, state.json mein #34 ka upload missing tha (haath se jod diya). Workflow ab `checkout ref: main` + conflict pe `-X theirs`.
- Asli Zoho screenshots (Gaurav ka CRM org60046315185, sirf sample data): assets/screens/crm/ mcp_server, leads_list, workflow_rules, webforms, mcp_for_ai_agents (Install menu: VS Code/Cursor/Other IDEs + link icon = server URL), api_names (Meetings = Events), catalyst_solutions. index.yaml mein click targets. Ye CRM edition: Functions/Blueprint/Zia setup nahi dikhte. Zoho Social account activate nahi hai (signup Claude nahi karta) - Social/Flow/Creator screens tab, jab Gaurav un apps ko on kare.
- Screenshot ka tareeka: Claude in Chrome `zoom` + save_to_disk (full-res PNG, scale ~1.05 of CSS px), JS se element rects -> targets; /home/claude/shots/add.py jaisa script.
- Flow clips: 1813-6 (3), 1827-12 (3), 1821-9 (6), 1828-13 (4), 1809-4 (6) - sab purane Shorts ke clips GitHub pe (robot assemble + schedule karta hai, ek push = ek run). Flow credits ~13 Oct 2:45 AM pe ~40 bache (month mein reset) - naye AI niche Shorts ke liye credits chahiye honge.
- Flow agent tip: prompt type karne ke baad pehla send click aksar register nahi hota - agent state check karo (Start generation vs Stop) aur dobara click; Stop kabhi mat dabao (request cancel ho jaati hai). Kuch clips mein gale ki chain aa jaati hai (Veo variance).

## Channel branding (12 Oct 2026)

YouTube channel ab "GSX Automation", handle @GSXAutomation (youtube.com/@GSXAutomation). Naya logo (GSX, navy/blue/yellow) + banner ("One real business problem. One quick automation fix.") + professional description (AI presenter disclosure + "not affiliated with Zoho" line) publish ho gaye. Channel name/logo mein "Zoho" jaan-boojh ke nahi (trademark). Purane 4 videos delete nahi kiye, sab Private. Duplicate robot upload MOwTQ0Q8qC4 bhi Private.

## 12 Oct 2026, raat ~1:45 IST (purana status)

YouTube pe scheduled: (1) Bill approvals - TuYUCh3cP6o, 12 Oct 7:30 AM (manual upload). (2) "Stop copying CRM/Books data to Excel" - Y1THCzxhr_Y, 12 Oct 7:35 AM (robot, naya editor v2 - QA pass). Baad mein: #7 duplicate leads (13 Oct 07:02), #9 Desk tickets (13 Oct 20:41).

Rukawat: Flow tab background mein ho to video file load nahi hoti (player sirf visible tab mein chalta hai).

Gemini free quota 11 Oct raat khatam hua (429) - scripts/TTS ke liye; din mein reset hota hai. TTS backup edge-tts laga diya.

Dashboard: https://claude.ai/artifact/8AcEp5wihXYFshpEPw4zJW . Scheduled task "GSX Shorts health check" roz 8:17, 11:17, 21:17 IST (push + e-mail on problem).

## Editor v2 (11 Oct raat) - user feedback ke baad

Presenter full-screen 9:16 dikhta hai (pura frame, body + haath), face pe tight crop / punch-in zoom nahi (composer.py).

Chehra sirf HOOK, PROBLEM, RESULT pe. FIX + STEP lines screens pe, awaaz Gemini TTS se (voice "Achird", wahi jo Flow avatar ki hai) - autopilot/tts.py.

CTA / "Follow" line hata di (writer prompt + flow.keep_lines). PROBLEM aur RESULT ek-ek chhoti line.

Shuru ki slowness: har clip ki speech loudness se tight trim + pace 1.1x (flow.speed). Flow prompts ab "medium-wide shot, knees up, hands visible, brisk pace, speak from first frame".

Screen sync: screen sirf us line pe jiski baat ho rahi hai; pehle pura screen, phir line ke end ki taraf button pe zoom.

QA min_score 75 -> 65. flow.max_batch 14 (manual run ek saath hafte ke Shorts bana sakta hai). Daily 10 AM run skip karta hai agar 2+ Shorts already clips ka wait kar rahe hain.

## Flow setup

Flow project "Oct 11 - 18:12" (labs.google/fx/tools/flow/project/9df382d1-38eb-402f-89ca-b98784c9192b). Character "Gaurav" = office blazer photo + voice "Achird custom". Agent settings: 9:16, Veo 3.1 Fast, x1, confirm = Never.

Credits: 11 Oct raat ~890 bache the. Veo 3.1 Fast = 20 credits / 8s clip, Lite = 10. Pro plan +50/din.

Clips GitHub tak kaise jaate hain: Flow grid mein thumbnail id = video media id. Editor page pe download -> 720p click karo, page ka fetch (flow-content.google/video/<id>?signed) blob deta hai (fetch wrap karke pakdo). Phir page pe ek button banao jo window.open se GitHub upload page khole (user click chahiye, warna popup block), us tab mein message listener + DataTransfer se file input, phir Commit. Ek Short ek commit - har run ek Short banata hai (ek run mein 3 Shorts = 90 min timeout ka risk).

## Timeline

Shuru mein: SadTalker / photo motion avatar, Gemini TTS, research/script/QA agents, screens.py Zoho UI screens.

11 Oct subah: Kaggle free GPU LatentSync lip-sync try kiya.

11 Oct dopahar: Kaggle/SadTalker/Veo/photo agent hata diye. Google Flow mode aaya.

11 Oct shaam: Flow avatar bana, 8 clips, run #20 assemble (QA 68/75), user ne video approve kiya, manual upload.

11 Oct raat: editor v2, batch of 12, dashboard, health-check task.

12 Oct: backup branch, niche v2 (AI + Zoho, global), research problem bank, multi-app screens, translations, closed-issue guard.

## Kaam ki files

channel.yaml - NICHE SWITCH (active_niche). niches/<niche>.yaml - us niche ki saari settings. research/problem_bank.yaml - real problems (yahan apni add karo). autopilot/flow.py - prompts, clip matching, face/TTS timeline. autopilot/composer.py - final layout. autopilot/tts.py - screen-part voice. autopilot/screens.py - Zoho / AI chat / API / code screens. assets/screens/index.yaml - asli Zoho screenshots. autopilot/writer.py - script agents + translations. autopilot/research.py - feeds + trend score + problem bank. state/state.json - robot ka state. .github/workflows/autopilot.yml - daily 10 AM IST + assemble on clip upload.

## 15 Nov 2026 (raat 00:10) – long video thumbnail + keywords
- Phone verify ho gaya, to long video -JyVV7LA4pA par custom thumbnail laga diya aur title / tags / description ke keywords update kar diye (workflow `longform-fix` on long-videos, run 43627830263 success).
- Naya title: "UAE E-Invoicing 2027 in Zoho Books: Step-by-Step Setup Guide"; 19 search tags (UAE e-invoicing, Zoho Books UAE, Peppol UAE, PINT AE, FTA e-invoicing, EmaraTax ...).
- Aage kisi bhi uploaded video ko edit karna ho: long-videos par docs/longform/fix-requests/<name>.json push karo (video_id, title, description_prepend, tags, thumb).
- Backup: backup-2026-11-15-before-video-fix-thumb.

## 15 Nov 2026 (raat 01-04) – daily robot (bina Flow / laptop / Claude chat)
- Long video -JyVV7LA4pA: thumbnail + keywords set. Naya robot: long-videos branch par shorts-daily + longform-daily
  (generic scenes, validator, 9:16 Shorts, thumbnail, 4K, upload), main par naya daily-robot.yml (brain 05:17 IST via
  Claude Code action + keeper 05:53/15:07 IST). Details + next step: docs/sessions/2026-11-15-daily-robot.md.
- Scheduled: Short ac2VsB7cqqU (15 Nov 07:30). Rendering: ZATCA Phase 2 long (15 Nov 18:30), 3 more Shorts.
- Gaurav ko karna hai: secret CLAUDE_CODE_OAUTH_TOKEN add karna (brain ke liye).
