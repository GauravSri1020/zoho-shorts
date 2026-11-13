# Long videos - plan v2 (Gaurav ne 13 Nov raat approve kiya)

Branch: `long-videos` (Shorts pipeline `main` pe alag chalta rahega - is branch se Shorts ka ek bhi file nahi chhoona).
Goal: channel MONETIZE - long videos se watch hours. Roz 1 long video (8-10 min, 16:9).

## Gaurav ke faisle (13 Nov 21:15-21:30 IST)

1. Har video = ek universal problem jo abhi news mein chal rahi hai (jaise UAE e-invoicing 1 Jan 2027). Facts sirf official / news source se, Shorts jaise strict rules (galat menu path = upload nahi).
2. Look: PODCAST FRAME - badi screen pe Zoho ki screen (recording), ek kone mein Gaurav ka chhota chehra, mic laga hua, lip-sync. Har din kuch badle: kapde, frame, background, chair, mic, kabhi headphones.
3. **Flow credits NAHI khaane** - roz max 1-2 Flow clips (base clip kone wale chehre ke liye / intro). Baaki sab free.
4. Screen recording: Gaurav Zoho (naya demo account, sample data, Books / Creator / jo chahiye) Chrome mein khol ke dega; Claude steps karega + tab record karega (browser ek baar "Share this tab" maangta hai - wo click Gaurav ka). Claude kabhi password nahi daalta.
5. Explainer scenes: GEOMETRIC CARTOON - gol sir, chaukor pet, danda tangein, bina aankh-munh (jaise "manual banda invoice le ke client ke paas jaata hai"). Plus whiteboard-style points. Background SIMPLE (grid hatao, saaf).
6. Har 20-40 s scene badle - 8 min mein interest loose na ho. Realistic lagna chahiye, AI jaisa nahi.
7. Voice: FREE voice cloning - Gaurav apni awaaz ka sample dega, poori video usi awaaz mein. Kaggle setup NAHI chahiye.
8. Quality: ~4K export (cartoons asli 4K, screen / Flow upscale).
9. Sab FREE. Claude / Gemini / open-source jo bhi kaam aaye.
10. Pipeline: researcher -> script + scenes -> (Gaurav ka Zoho) screen recording -> voice -> lip-sync -> editor -> QA -> GitHub -> YouTube schedule. Pehle Gaurav sample review karega, tab tak YouTube pe UPLOAD NAHI.

## Free tools (scheduled run ko verify karna hai - commercial use allowed ho, channel monetized hoga)

- Cartoon / whiteboard / chapter cards: HTML+SVG `render(t)` -> Playwright frame screenshots -> ffmpeg (prototype: `longform/prototype/`). 4K = viewport 1920x1080, deviceScaleFactor 2. Manim bhi chalega (runner pe `apt install libpango1.0-dev`), par HTML wala repo ke `screens.py` jaisa hai.
- Voice clone (Gaurav ki awaaz, uski marzi se): license dekh ke chuno. Commercial OK hone chahiye. Candidates: Chatterbox (Resemble AI, MIT - verify), OpenVoice V2 (MIT - verify). NAHI: XTTS-v2 (Coqui CPML = non-commercial), F5-TTS weights (CC-BY-NC). Jab tak sample nahi aata: Kokoro (Apache 2.0) ya Piper - ek hi awaaz poori video mein.
- Lip-sync (kone ka chhota chehra, CPU pe GitHub runner, 6 h limit): license check zaroori - Wav2Lip = research/non-commercial (NAHI). MuseTalk / LatentSync ka license + CPU speed verify karo. Kone ka chehra chhota hai (~360 px) to low-res lip-sync bhi chalega. Agar koi free + commercial + CPU wala nahi mila: kone mein base clip loop + audio-reactive munh nahi; us case mein chehra sirf intro/outro (Flow) mein, baaki faceless.
- Screen: asli recording (Gaurav ka Zoho) - jab tak nahi milti, `assets/screens/books/*.png` (asli screenshots) pe smooth zoom / pan / cursor / click animation (Ken Burns), "recording placeholder" ke taur pe.
- Music: repo ka `autopilot/music.py` jaisa royalty-free.

## Scene types

| Type | Kya dikhta hai | Kab |
|---|---|---|
| HOOK | Flow intro clip (Gaurav full face) ya cartoon | 0:00-0:20 |
| PODCAST | badi Zoho screen + kone mein Gaurav (mic) + lower-third caption | demo steps |
| CARTOON | geometric banda, problem ki kahani | problem / "why it matters" |
| BOARD | whiteboard points / diagram draw-on | timeline, penalties, checklist |
| CHAPTER | chhota title card | har chapter ke shuru mein |
| OUTRO | Flow outro / subscribe | end |

## Pehli video (sample, Gaurav review karega)

"UAE E-Invoicing in Zoho Books: everything to do before 1 January 2027" - facts HISTORY 12 Nov (Zoho = MoF accredited ASP; AED 50M se kam: ASP 31 Mar 2027, live 1 Jul 2027; penalties AED 5,000/month, AED 100/invoice) - scheduled run ko DOBARA verify karna hai official source se.

## Content calendar (aage)

- UAE e-invoicing (sample) -> ZATCA Phase 2 -> Zoho Books payments + reminders -> Zoho CRM web leads. Har ek ke Shorts pehle se channel pe hain (unhe long video se link karna).

## Code (is branch mein, `longform/`)

- `longform/research.py` (topic + facts), `longform/script.py` (scenes JSON), `longform/scenes/*.html` (cartoon / board / chapter templates), `longform/render.py` (Playwright frames -> ffmpeg), `longform/voice.py`, `longform/lipsync.py`, `longform/compose.py` (16:9, 4K), `longform/qa.py`.
- Workflow: `.github/workflows/longform.yml` (sirf workflow_dispatch jab tak Gaurav approve na kare; koi upload nahi).

## Gaurav se abhi chahiye

- Apni awaaz ka sample (1-2 min, saaf, bina music) - voice clone ke liye.
- Pichhli chat ka reference video link (wo chat save nahi hui).
- Zoho demo account (Books pehle) Chrome mein khula.
- 1-2 Flow clips: podcast setup (mic, kone wala frame) - Gaurav ke Flow mein.
