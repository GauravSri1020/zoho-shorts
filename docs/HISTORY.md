# Project history and current status

Is file ko har session ke end pe update karo, taaki agla chat yahin se shuru kare.

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

channel.yaml - saari settings. research/problem_bank.yaml - real problems (yahan apni add karo). autopilot/flow.py - prompts, clip matching, face/TTS timeline. autopilot/composer.py - final layout. autopilot/tts.py - screen-part voice. autopilot/screens.py - Zoho / AI chat / API / code screens. assets/screens/index.yaml - asli Zoho screenshots. autopilot/writer.py - script agents + translations. autopilot/research.py - feeds + trend score + problem bank. state/state.json - robot ka state. .github/workflows/autopilot.yml - daily 10 AM IST + assemble on clip upload.
