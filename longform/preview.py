"""Quick stills for review: python -m longform.preview out/uae/plan.json out/uae/stills [s04,s10] [n_per_scene]"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main(plan, outdir, only="", n=4):
    scenes = json.loads(Path(plan).read_text())
    only = set(x for x in only.split(",") if x)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=0.5)
        page.on("console", lambda m: print("console:", m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: print("PAGEERROR:", e))
        page.goto((ROOT / "longform/scenes/stage.html").as_uri())
        page.evaluate("document.fonts.ready.then(()=>true)")
        for s in scenes:
            if only and s["id"] not in only:
                continue
            page.evaluate("d => window.setup(d)", {**s, "root": ROOT.as_uri()})
            page.wait_for_timeout(200)
            ts = [s["cues"][min(i, len(s["cues"]) - 1)]["e"] - 0.2 for i in range(len(s["cues"]))] if n == 0 else \
                [s["dur"] * (k + 0.5) / n for k in range(n)]
            for k, t in enumerate(ts):
                page.evaluate("t => window.render(t)", t)
                page.screenshot(path=str(out / f"{s['id']}_{k}.png"))
        b.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", int(sys.argv[4]) if len(sys.argv) > 4 else 4)
