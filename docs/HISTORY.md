# Project history and current status

Is file ko har session ke end pe update karo, taaki agla chat yahin se shuru kare.

## Abhi kahan hain (11 Oct 2026, raat)

Engine: Google Flow mode (autopilot/flow.py). Face wale clips Flow (Veo 3.1 Fast, 9:16) mein tere avatar se bante hain, baaki sab robot karta hai.

Pending Short: jobs/20261011-1326-1 "Stop Paying Extra Zoho Books Seats for Bill Approvals" - status waiting_for_clips (8 clips chahiye, issue #2).

Blocker: Google Flow mein avatar (Character) abhi bana hi nahi hai. Ek saaf photo chahiye avatar banane ke liye.

Zoho screens (screens.py) wala look theek hai - user ne approve kiya.

## Agle steps (order mein)

Step 1: Flow > Characters > Upload photo > avatar banao (naam: Gaurav).

Step 2: jobs/20261011-1326-1/PROMPTS.md ke 8 prompts Flow mein chalao, avatar select karke, 9:16, Veo 3.1 Fast.

Step 3: 8 clips download karke jobs/20261011-1326-1/clips/ mein upload > Commit. Workflow apne aap assemble karta hai.

Step 4: Actions run dekho; QA pass ho to YouTube pe schedule hota hai (job.json mein abhi upload=false hai - check karo).

Step 5: YouTube Studio mein video Scheduled dikhe, AI label ON ho.

## Timeline

Shuru mein: SadTalker / photo motion avatar, Gemini TTS, research/script/QA agents, screens.py Zoho UI screens.

11 Oct subah: Kaggle free GPU LatentSync lip-sync try kiya.

11 Oct dopahar: Kaggle/SadTalker/Veo/photo agent sab hata diye. Google Flow mode aaya: robot roz PROMPTS.md + issue banata hai, clips upload hote hi assemble + QA + YouTube.

11 Oct: clips ~12 se ~8 kiye (sentence pe break). Presenter look rotate hota hai (har Short ek look, saare clips mein same).

11 Oct: purane jobs (0537, 0556, 1318) ke job.json delete kiye. Sirf 1326-1 active hai.

## Kaam ki files

channel.yaml - saari settings. autopilot/flow.py - prompts + clip matching + watermark hide. autopilot/editor.py - final edit. autopilot/screens.py - Zoho screens. state/state.json - robot ka state. .github/workflows/autopilot.yml - daily 10 AM IST + assemble on clip upload.
