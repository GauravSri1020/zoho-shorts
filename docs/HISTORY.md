# Project history and current status

Is file ko har session ke end pe update karo, taaki agla chat yahin se shuru kare.

## RULE: pehle backup, phir kaam (Gaurav ka standing order)

Gaurav jab bhi kuch bhi change karne bole: SABSE PEHLE backup - `backup-YYYY-MM-DD-<kya-badal-rahe-ho>` branch main se banao (aur agar video ka kaam hai to latest Short ka artifact download karo). Tabhi code chhuo. Kuch bigde to us branch se purana code wapas lo.

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
