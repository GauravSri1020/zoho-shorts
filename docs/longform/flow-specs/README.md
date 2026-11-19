# Flow avatar Shorts (Gaurav's order 20 Nov 2026: Shorts ONLY from Flow avatar clips, no cartoon Shorts)

One file per Short: `docs/longform/flow-specs/<id>.json` (written by the script-writer agent, facts from a research file):
{
  "id": "flow-YYYYMMDD-<slug>", "priority": "news|evergreen", "structure": "...", "hook_type": "...",
  "title": "<= 90 chars, keyword first, #Shorts", "description": "summary + sources with URLs + checked date +
   AI-disclosure line (+ Not affiliated with Zoho line when Zoho is named) + hashtags", "tags": [...],
  "banner": "TOP BANNER · 3-4 WORDS", "source": "Sources: ... (date)",
  "look": "one outfit + place + grooming sentence, same in every clip",
  "clips": [{"file": "c1.mp4", "say": "spoken sentence for Flow (numbers as words)",
             "text": "caption form (numbers as digits)", "lower": ["NAME", "role"] | null, "gesture": "..."}]
}

Who makes them:
1. Brain (daily-robot, 05:17 IST) writes 2-3 specs per day (1 = trending news) + docs/longform/flow-queue/<date>.md.
2. A Claude session with Gaurav's Chrome (scheduled task "Flow Shorts daily", or any live chat) opens Flow
   (main account gauravsri069 first, then Golu Sri /u/1 when credits are low), generates every clip
   (Veo 3.1 Fast, 9:16, x1, avatar "Me", 20 credits each), checks each clip (look, no tilak, lips, line complete),
   uploads them to branch `flow-clips` folder `flow/<date>/<id>/`, builds with
   `python -m longform.news_short <spec> <clips_dir> out.mp4`, looks at a contact sheet, then schedules it:
   - Actions available: push the mp4 to `longform-previews/previews/<id>.mp4` + meta + upload-request
     (`"upscale": false`) -> workflow longform-upload.
   - Actions blocked (billing): YouTube Studio upload in the browser, schedule time, AI-disclosure "altered content" yes.
Slots (IST): news Short 13:30 (or the next free slot if the news is hot), evergreen 07:30 / 21:30.
