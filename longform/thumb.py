"""Thumbnail from the script's "thumb" block (generic template, same look as the UAE one).

  python -m longform.thumb docs/longform/scripts/<id>.json out/<id>-thumb.jpg

script "thumb": {"chip": "UAE · 2027", "l1": "E-INVOICING", "l2": "ZOHO BOOKS", "l3": "SETUP", "pill": "BEFORE 1 JAN 2027",
                 "pose": "point_up" (assets/presenter), "accent": "#ffd23f" (optional)}
"""
import json
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(script, out):
    th = json.loads(Path(script).read_text()).get("thumb") or {}
    if not th.get("l1"):
        raise SystemExit("script has no thumb.l1 - no thumbnail")
    from playwright.sync_api import sync_playwright
    url = (ROOT / "longform/thumb/template.html").as_uri() + "#" + urllib.parse.quote(json.dumps(th))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(url)
        pg.wait_for_selector("body[data-ready]", timeout=15000)
        pg.wait_for_timeout(300)
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=str(out), type="jpeg", quality=92)
        b.close()
    print(f"[thumb] {out} ({Path(out).stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
