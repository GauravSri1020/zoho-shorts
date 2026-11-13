# Prototype: geometric cartoon scene (13 Nov 2026)

`cartoon_invoice.html` draws one scene with a deterministic `window.render(t)` (SVG). `render.js` opens it in
Playwright (1920x1080, deviceScaleFactor 2 = 3840x2160), screenshots every frame (30 fps, 7 s) to `frames/`.
Then: `ffmpeg -framerate 30 -i frames/f%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p sample_4k.mp4`.
Gaurav saw the 7 s sample and said OK; to do: simpler background (no grid), better font (Patrick Hand / Kalam, OFL),
smoother motion, more scenes. Not wired into anything yet.
