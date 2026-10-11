# Project history and current status

Is file ko har session ke end pe update karo, taaki agla chat yahin se shuru kare.

## Abhi kahan hain (12 Oct 2026, raat ~1:45 IST)

YouTube pe scheduled: (1) Bill approvals - TuYUCh3cP6o, 12 Oct 7:30 AM (manual upload). (2) "Stop copying CRM/Books data to Excel" - Y1THCzxhr_Y, 12 Oct 7:35 AM (robot, naya editor v2 - QA pass). Dono same subah hain (slot clash) - chahe to Studio mein ek ko shift karo.

Clips upload ho chuke (robot assemble + schedule karega): 20261011-1806-2 (CRM lead tasks), 1812-5 (duplicate leads), 1816-7 (Zoho Desk tickets).

Flow mein clips BAN chuke par upload BAAKI: 1813-6 (Creator PDF: H/P/R), 1807-3 (restaurant recipes: H/P/R), 1823-10 (payment reminders: H/P/R, Flow agent se), 1824-11 (CRM mandatory fields: H/P/R, agent se), 1827-12 (low stock: sirf HOOK). Ye Flow project ke grid mein hain; har video ke edit page pe prompt dikhta hai ("He says ... \"line\"").

Clips bilkul nahi bane: 1827-12 PROBLEM+RESULT, 1809-4 (6 clips), 1821-9 (6 clips), 1828-13 (3 clips).

Rukawat: Flow tab background mein ho to video file load nahi hoti (player sirf visible tab mein chalta hai), isliye raat ko unattended upload ruk gaya. Agli baar Flow tab ko aage (visible) rakh ke Claude ko bolo "baaki Flow clips upload kar do".

Gemini free quota 11 Oct raat khatam hua (429) - scripts/TTS ke liye; din mein reset hota hai. TTS backup edge-tts laga diya.

Dashboard: https://claude.ai/artifact/8AcEp5wihXYFshpEPw4zJW . Scheduled task "GSX Shorts health check" roz 8:17, 11:17, 21:17 IST (push + e-mail on problem).

## Editor v2 (11 Oct raat) - user feedback ke baad

Presenter full-screen 9:16 dikhta hai (pura frame, body + haath), face pe tight crop / punch-in zoom nahi (composer.py).

Chehra sirf HOOK, PROBLEM, RESULT pe. FIX + STEP lines Zoho screens pe, awaaz Gemini TTS se (voice "Achird", wahi jo Flow avatar ki hai) - autopilot/tts.py.

CTA / "Follow" line hata di (writer prompt + flow.keep_lines). PROBLEM aur RESULT ek-ek chhoti line.

Shuru ki slowness: har clip ki speech loudness se tight trim + pace 1.1x (flow.speed). Flow prompts ab "medium-wide shot, knees up, hands visible, brisk pace, speak from first frame".

Screen sync: screen sirf us line pe jiski baat ho rahi hai; pehle pura screen, phir line ke end ki taraf button pe zoom.

QA min_score 75 -> 65. flow.max_batch 14 (manual run ek saath hafte ke Shorts bana sakta hai). Daily 10 AM run skip karta hai agar 2+ Shorts already clips ka wait kar rahe hain.

## Flow setup

Flow project "Oct 11 - 18:12" (labs.google/fx/tools/flow/project/9df382d1-38eb-402f-89ca-b98784c9192b). Character "Gaurav" = office blazer photo + voice "Achird custom". Agent settings: 9:16, Veo 3.1 Fast, x1, confirm = Never.

Credits: 11 Oct raat ~890 bache the. Veo 3.1 Fast = 20 credits / 8s clip, Lite = 10. Pro plan +50/din.

Clips GitHub tak kaise jaate hain: Flow tab mein video blobs fetch -> window.open se GitHub upload page -> postMessage -> DataTransfer se file input -> Commit.

## Pending / next

Clips bana ke 12 jobs mein daalna (jitne credits allow karein). Phir dashboard pe check.

Long term: Flow ka koi API nahi, isliye clips roz automatically nahi ban sakte bina browser ke. Options: (a) Claude ko bolo "Flow clips bana do" jab dashboard pe "Needs clips" dikhe, (b) Veo API (paid, billing key) wapas lagana.

GitHub Actions: repo private hai, free minutes limited (2000/mahina).

## Timeline

Shuru mein: SadTalker / photo motion avatar, Gemini TTS, research/script/QA agents, screens.py Zoho UI screens.

11 Oct subah: Kaggle free GPU LatentSync lip-sync try kiya.

11 Oct dopahar: Kaggle/SadTalker/Veo/photo agent hata diye. Google Flow mode aaya.

11 Oct shaam: Flow avatar bana, 8 clips, run #20 assemble (QA 68/75), user ne video approve kiya, manual upload.

11 Oct raat: editor v2, batch of 12, dashboard, health-check task.

## Kaam ki files

channel.yaml - saari settings. autopilot/flow.py - prompts, clip matching, face/TTS timeline. autopilot/composer.py - final layout. autopilot/tts.py - screen-part voice. autopilot/screens.py - Zoho screens. autopilot/writer.py - script agents. state/state.json - robot ka state. .github/workflows/autopilot.yml - daily 10 AM IST + assemble on clip upload.
