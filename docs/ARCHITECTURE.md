# Architecture (for developers)

Fully automatic YouTube Shorts pipeline for a Hinglish "Zoho fix" channel. Runs on GitHub Actions
(`.github/workflows/autopilot.yml`), configured by `channel.yaml`, state kept in `state/`.

## Tasks (`python -m autopilot.main <task>`)

| Task | When | What |
|---|---|---|
| `daily` | 10:00 IST cron | research -> script -> voice -> avatar -> video -> QA -> scheduled upload |
| `assemble` | push to `jobs/*/clips/**` | manual Gemini mode only: uploaded clips -> finished Short -> QA -> upload |
| `comments` | every 3 h | replies to new comments |
| `photos` | Sunday | photo agent: new photos of the presenter (encrypted bundle) |

## Pipeline of one Short

```
research.py  -> real problems from RSS feeds (Reddit, Stack Overflow, Google News)
writer.py    -> scout angle, write script (lines with beats HOOK/PROBLEM/FIX/STEP n/RESULT/CTA), script QA
voice.py     -> AI voice (Gemini TTS, edge-tts backup) -> voice.wav
editor.py    -> whisper word timings, aligned to the exact script words
avatar.py    -> presenter video, as long as the voice (engine from channel.yaml -> avatar.engine)
composer.py  -> final 1080x1920 Short: title, middle panel (avatar <-> Zoho screens from screens.py),
                word-timed captions, music (music.py)
benchmark.py -> QA agent (Gemini watches the Short, scores vs reference Shorts) -> upload gate
google_apis.py, schedule.py -> scheduled YouTube upload (AI label on)
state.py     -> state/state.json (topics used, slots, comments seen)
notify.py    -> Telegram / email, only on problems
```

## Avatar engines (`channel.yaml -> avatar.engine`)

| Engine | Module | Cost | Notes |
|---|---|---|---|
| `gemini_manual` | `manual.py` + `veo.assemble` | free (Gemini Pro app) | daily run writes `jobs/<id>/PROMPTS.md`; clips uploaded to `jobs/<id>/clips/` trigger `assemble` |
| `veo` | `veo.py` | paid Veo API (`VEO_API_KEY`) | fully automatic, clips generated in parallel |
| `sadtalker` | `avatar.py` | free, CPU, slow | lip-synced photo; fallback for `veo` |
| `photo` | `avatar.py` | free | photo + camera motion, last fallback (QA blocks upload) |

### How generated clips are lip-synced to our voice (`veo.py`)
1. `pieces()` – on-camera lines (not Zoho screens), split so each fits one 8 s clip.
2. Each clip says that line (Veo / Gemini). Its own audio is discarded.
3. `_anchors()` – whisper finds the words in the clip; each script word is paired
   (TTS time, clip time), smoothed and clamped (0.45x–2.2x speed).
4. `assemble()` – frame-by-frame re-timing onto the TTS timeline; one continuous avatar video is
   returned, so `composer.py` is unchanged.

## Manual Gemini mode flow (`manual.py`)
```
daily (prepare)          you                          push -> assemble (finish)
script + voice    ->  Gemini app: photo + prompt  ->  re-time clips, compose, QA,
jobs/<id>/PROMPTS.md  download clips, upload to       upload, delete jobs/<id>
jobs/<id>/job.json    jobs/<id>/clips/01.mp4 ...
jobs/<id>/voice.wav
```

## Secrets / variables
`GEMINI_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `AVATAR_KEY`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, optional `VEO_API_KEY` (paid Veo only).
Variables: `GEMINI_MODEL`, `AVATAR_ENGINE` (overrides channel.yaml), `VEO_MODELS`.
