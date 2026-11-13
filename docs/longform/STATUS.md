# Long videos - STATUS

SAMPLE: DONE (13/14 Nov 2026 night run) - waiting for Gaurav's review. NOT uploaded to YouTube.

## Sample 1: "UAE E-Invoicing in Zoho Books: Everything to Do Before 1 January 2027"
- 7 min 36 s, 16:9, **2560x1440 (1440p)** 30 fps, H.264 + AAC, loudness -15.1 LUFS (QA window -16.5..-12.5), 54.8 MB. 4K was not rendered tonight: this 2-core box
  renders ~10 s of video per minute at 1440p (4K would be ~2.5 h + encode). The workflow `longform.yml` (input scale = 2) can render 4K on GitHub.
- Preview file: branch `longform-previews` -> `previews/uae-einvoicing-1440p.mp4` (+ contact sheet).
- QA (longform/qa.py): no black frames, no dead air > 1.2 s, loudness OK; glitch check (longform/glitch.py) for half-painted frames.
- 23 scenes, change every ~5-40 s: HOOK, 5 CHAPTER cards, CARTOON x5 (old way vs new, 5-corner model, 14 business days, penalties,
  celebrate), BOARD x8 (scope, timeline, Zoho = accredited ASP, EmaraTax flow, Peppol ID formula, customer/item data, checklist),
  PODCAST x4 (Zoho Books screen + presenter corner), OUTRO.

## What is PLACEHOLDER in the sample
- **Screen**: animated real screenshots (assets/screens/books, India org "Helios") - zoom / cursor / clicks / highlight. Real UAE-org
  recording needed (docs/longform/RECORDING_TODO.md). The UAE E-Invoicing settings page itself is shown as a checklist overlay.
- **Presenter corner**: Gaurav's cut-out photos (assets/presenter) with mic, breathing / sway, voice meter - no lip-sync (no licence-OK
  CPU lip-sync exists, see TOOLS.md).
- **Voice**: Kokoro `am_michael` (Apache-2.0) - US male voice until Gaurav's sample -> Chatterbox clone (MIT).
- Zoho Books menu labels come from a guide citing Zoho's help page (Zoho's page could not be opened) -> confirm on screen when recording.
- Penalty amounts AED 100 / invoice and the AED 50,000 cap: from Crowe + Sovos summaries of Cabinet Decision 173/2026 (official PDF
  not readable tonight; FTA confirms AED 5,000 / month). Re-check before upload.

## Chapters (for the description)
0:00 UAE e-invoicing in 30 seconds
0:36 What is changing
2:02 Who goes live when
3:07 What it costs if you miss it
3:43 Setting it up in Zoho Books
6:22 Your checklist

## Needed from Gaurav
1. Review the sample (what to change in look / pace / voice).
2. Voice sample 1-2 min (clean, no music) -> voice clone.
3. Reference video link from the lost chat.
4. Zoho Books **UAE** demo org open in Chrome (sample data) -> Claude records R1-R7.
5. 1-2 Flow clips: podcast set-up (him at a mic) for the corner / intro.

## Next step (exact)
Gaurav reviews the sample -> Claude applies his notes in longform/scenes + script; with his voice sample: add
longform/voice.py engine "chatterbox"; with the UAE demo org: record R1-R7 and add a `video` source to PODCAST scenes; then 4K render via
workflow longform.yml and only then YouTube (after his OK).
