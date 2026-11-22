# Trending-style news Short (prototype, 22 Nov 2026) - NOT wired into any workflow

Gaurav: "video theek hai lekin acchi nahi lagi - apne hisaab se trending style bana". Sample: Nvidia worst week (37.9 s).
Style: dark grid + colour glow, BREAKING pill + ticker chip, progress bar, kinetic Anton numbers that count up and slam,
crash chart, split screen, word-by-word yellow captions (3 words), punch zoom + shake on hits, whoosh/impact/tick SFX,
ducked pulse bed. Kokoro am_fenrir 1.12. Build: lines.json -> voice (per line) -> words.py (data.json) ->
render.py full (Playwright frame-by-frame, ~9 min) -> SFX mix + loudnorm. Scenes in page.html are hand-made per story.
Next step if Gaurav likes it: make scenes data-driven (scene kinds: counter, bars, news card, crash chart, split, cta).
