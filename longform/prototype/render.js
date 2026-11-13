const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await p.goto('file://' + __dirname + '/cartoon_invoice.html');
  const fps = 30, dur = 7;
  require('fs').mkdirSync('frames', { recursive: true });
  for (let i = 0; i < fps * dur; i++) {
    await p.evaluate(t => window.render(t), i / fps);
    await p.screenshot({ path: `frames/f${String(i).padStart(4, '0')}.png` });
  }
  await b.close();
})();
