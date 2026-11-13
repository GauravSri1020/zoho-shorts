# longform/ - long 16:9 videos (branch long-videos only; Shorts pipeline on main is untouched)

```
python longform/voice.py docs/longform/scripts/<id>.json out/voice              # Kokoro TTS, one wav per line
python -m longform.render docs/longform/scripts/<id>.json --voice out/voice --out out/video --scale 1.3334   # 1440p (2 = 4K)
python -m longform.preview out/video/plan.json out/stills "" 0                 # stills at the end of every line (review)
python -m longform.qa out/video/<id>.mp4 --voice out/video/voice.wav           # strict QA
```
- `scenes/stage.html` + `lib.js` (geometric character, props, board helpers) + `scenes.js` (HOOK, CHAPTER, CARTOON kinds, BOARD
  kinds, PODCAST, OUTRO). Every scene is a pure function of time: `window.setup(data)` then `window.render(t)`.
- Script JSON (docs/longform/scripts): scenes with `type`, `lines` (one TTS sentence each = one animation cue) and `visual`.
  PODCAST actions: `{cue, at, screen, target|box, zoom}` (targets from assets/screens/index.yaml), overlays `panel|send|status|inbox`.
- Timing: each line is synthesised alone -> exact cue times -> captions + animations follow the voice.
- Segments are cached per scene in `<out>/seg/` (delete one file to re-render that scene; `--only s04,s10` forces).
- `prototype/` = the first 7 s test (13 Nov).
