"""Cover / thumbnail for a Short (Gaurav, 2 Nov 2026).

In the Shorts feed / channel grid YouTube shows a frame of the video before anyone taps it. That frame used to be a
plain screen card, so nobody stopped. Now every Short opens on a COVER, like a real creator thumbnail:

    +--------------------------------+
    |        @GSXAutomation          |
    |   BIG 2-3 LINE TITLE, ONE      |   white, heavy, the key words on a yellow marker
    |   [KEY WORDS] HIGHLIGHTED      |
    |              +-----------+     |
    |   Gaurav     |  Claude   | $$  |   the Short's own Claude screen in a tilted card + money sticker
    |  (cut-out,   |  screen   |     |
    |   pointing)  +-----------+     |
    +--------------------------------+

  * cover(sc, workdir, screen_png) -> cover.png (1080x1920) + cover.jpg (YouTube custom thumbnail, < 2 MB)
  * composer puts cover.png on the first ~1 s of the video (gentle zoom, then fades into the Short), so the
    frame YouTube shows first IS the thumbnail; flow.py also sets cover.jpg as the custom thumbnail (best effort).
Presenter photos: assets/presenter/ (cut from his own Flow avatar clips) - index.yaml says which side he stands on.
"""
import hashlib
import html as h
import random
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSE_DIR = ROOT / "assets" / "presenter"
FONT = ROOT / "assets" / "fonts" / "Poppins-Bold.ttf"
W, H = 1080, 1920
INTRO = 1.0  # seconds the cover stays on screen at the start of the Short (the hook voice already plays under it)

_MONEY = re.compile(r"\$\s?\d[\d,.]*\s?[kK]?(?:\s?(?:/|a|per)\s?(?:mo(?:nth)?|client|week|wk|hour|hr|project)\b)?",
                    re.I)


def poses():
    try:
        return (yaml.safe_load((POSE_DIR / "index.yaml").read_text()) or {}).get("poses") or []
    except Exception:
        return []


def cover_text(sc):
    """3-7 words for the cover. The script's own 'thumb_text' (writer asks for it), else the title, shortened."""
    t = str(sc.get("thumb_text") or "").strip()
    if not t:
        t = str(sc.get("title") or sc.get("hook_text") or "").replace("#Shorts", "").strip()
        if len(t) > 42 and ":" in t:  # "Sell Podcast Clips with Claude: $500 a Month" -> the part before ':'
            t = t.split(":")[0].strip()
        # "... with Claude" at the end: the Claude screen already says it - spend the big letters on the subject
        t = re.sub(r"\s+(?:with|using)\s+Claude(?:\s+(?:Code|Projects?|Skills?))?$", "", t, flags=re.I) or t
    t = re.sub(r"\s+", " ", t).strip()
    ws = t.split()
    if len(ws) > 7:  # a cover is read in half a second: cut at "that / which / who / -" or keep 7 words
        cut = next((i for i, w in enumerate(ws) if i >= 3 and w.lower().strip("*") in ("that", "which", "who", "-", "when",
                                                                                       "so", "because")), None)
        ws = ws[:cut] if cut else ws[:7]
        while len(ws) > 3 and ws[-1].lower().strip("*") in ("a", "an", "the", "to", "for", "with", "of", "and", "your",
                                                             "their", "in", "on", "that"):
            ws.pop()
    return " ".join(ws)


def money_badge(sc, text):
    """'$2,000/mo' from the title / hook / SELL card - only when the cover text does not already say a price."""
    if "$" in text:
        return ""
    pool = [sc.get("title"), sc.get("hook_text")] + [l.get("card") for l in (sc.get("lines") or [])
                                                     if str(l.get("beat", "")).upper() in ("SELL", "MATH", "HOOK")]
    for s in pool:
        m = _MONEY.search(str(s or ""))
        if m:
            b = m.group(0).strip()
            b = re.sub(r"\s*(?:a|per|/)\s*(?:month|mo)\b", "/mo", b, flags=re.I)
            b = re.sub(r"\s+(?:a|per)\s+", "/", b, flags=re.I)
            return b.replace(" ", "")[:12]
    return ""


def _title_html(text):
    """*marked* words (from the writer) or money / numbers go on the yellow marker; else the last 2 words."""
    if "*" in text:
        out = re.sub(r"\*([^*]+)\*", lambda m: f"<mark>{h.escape(m.group(1))}</mark>", h.escape(text).replace("&#x27;", "'"))
        return out.replace("*", "")
    ws = text.split()
    hit = [i for i, w in enumerate(ws) if re.search(r"[$\d]", w)]
    if not hit:
        k = 2 if len(ws) >= 4 else 1
        hit = list(range(len(ws) - k, len(ws)))
    a, b = min(hit), max(hit)
    return (h.escape(" ".join(ws[:a])) + f" <mark>{h.escape(' '.join(ws[a:b + 1]))}</mark> "
            + h.escape(" ".join(ws[b + 1:]))).strip()


def _pick_pose(sc, seed=None):
    ps = [p for p in poses() if (POSE_DIR / p.get("file", "")).exists()]
    if not ps:
        return None, "left"
    key = seed if seed is not None else int(hashlib.md5(str(sc.get("title", "")).encode()).hexdigest()[:8], 16)
    rng = random.Random(key)
    p = rng.choice(ps)
    side = p.get("side", "any")
    if side not in ("left", "right"):
        side = rng.choice(["left", "right"])
    return p, side


def cover(sc, workdir: Path, screen_png=None, accent="#D97757", handle="", label="Claude", seed=None):
    """Renders cover.png + cover.jpg into workdir and returns the PNG path (None if the browser is missing)."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    text = cover_text(sc)
    badge = money_badge(sc, text)
    pose, side = _pick_pose(sc, seed)
    pw = int((pose or {}).get("width") or 760)
    me = (f'<img class="me" src="{(POSE_DIR / pose["file"]).resolve().as_uri()}">' if pose else "")
    shot = (f'<img class="shot" src="{Path(screen_png).resolve().as_uri()}">' if screen_png and Path(screen_png).exists()
            else f'<div class="chat"><div class="you">{h.escape(text)}</div><div class="ans">Here is how, step by step '
                 f'&mdash; with the exact prompt.</div><div class="box">Reply to Claude...</div></div>')
    # screen on the side opposite the presenter; he overlaps its lower corner a little
    scr_x = 430 if side == "left" else 60
    # the cut-outs end where the Flow frame ended (a straight edge at the shoulder): fade the edge that faces the screen
    fade = "to right" if side == "left" else "to left"
    me_css = (("left:-70px" if side == "left" else "right:-70px")
              + f";-webkit-mask-image:linear-gradient({fade},#000 86%,transparent 100%)")
    tilt = 4 if side == "left" else -4
    # money sticker on the screen's far corner: top-right when he stands left; bottom-left when he stands right
    # (top-left would hide the "Claude" bar)
    badge_x, badge_y = ((W - 300), 660) if side == "left" else (24, 1360)
    bmain, _, bunit = badge.partition("/")  # "$2,000" big, "PER MONTH" small under it
    bunit = {"mo": "PER MONTH", "client": "PER CLIENT", "week": "PER WEEK", "wk": "PER WEEK", "hour": "PER HOUR",
             "hr": "PER HOUR", "project": "PER PROJECT"}.get(bunit.lower(), bunit.upper())
    bsize = 84 if len(bmain) <= 4 else 70 if len(bmain) <= 6 else 56
    arrow = (f'<svg class="arrow" viewBox="0 0 220 160" style="{"left:200px" if side == "left" else "right:200px;transform:scaleX(-1)"}">'
             '<path d="M10 140 C 60 40, 120 20, 190 40" fill="none" stroke="#FFD400" stroke-width="14" '
             'stroke-linecap="round"/><path d="M160 12 L 205 42 L 158 70" fill="none" stroke="#FFD400" '
             'stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    tag = h.escape(("@" + handle.lstrip("@")) if handle else "")
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
    @font-face{{font-family:Pop;src:url('{FONT.resolve().as_uri()}')}}
    *{{box-sizing:border-box}}
    body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:Pop,'Noto Sans',sans-serif;
         background:linear-gradient(165deg,#0A0F1F 0%,#141C38 55%,#0A0F1F 100%);position:relative}}
    .g1{{position:absolute;width:1100px;height:1100px;left:-300px;top:-380px;border-radius:50%;
         background:radial-gradient(circle,{accent}70 0%,transparent 62%)}}
    .g2{{position:absolute;width:1200px;height:1200px;right:-420px;bottom:-300px;border-radius:50%;
         background:radial-gradient(circle,{accent}55 0%,transparent 60%)}}
    .grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),
           linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:60px 60px}}
    .tag{{position:absolute;top:140px;left:0;right:0;text-align:center;color:#fff;opacity:.85;font-size:32px;
          letter-spacing:1px}}
    .title{{position:absolute;top:205px;left:50px;right:50px;height:500px;display:flex;align-items:center;
            justify-content:center;text-align:center;color:#fff;text-transform:uppercase;line-height:1.04;
            font-size:120px;text-shadow:0 8px 0 #000,0 0 40px rgba(0,0,0,.6);word-break:normal}}
    .title mark{{background:#FFD400;color:#0A0F1F;text-shadow:none;padding:0 16px;border-radius:14px;
                 -webkit-box-decoration-break:clone;box-decoration-break:clone;display:inline}}
    .screen{{position:absolute;left:{scr_x}px;top:760px;width:590px;height:800px;border-radius:38px;
             background:#FAF9F5;border:10px solid #fff;overflow:hidden;transform:rotate({tilt}deg);
             box-shadow:0 30px 80px rgba(0,0,0,.65),0 0 0 4px {accent},0 0 120px {accent}88}}
    .bar{{height:70px;background:#F0EEE6;display:flex;align-items:center;gap:14px;padding:0 26px;
          font-size:30px;color:#3D3929;border-bottom:2px solid #E5E1D6}}
    .dot{{width:22px;height:22px;border-radius:50%;background:#D97757}}
    .shot{{width:100%;height:calc(100% - 70px);object-fit:cover;object-position:top center;display:block}}
    .chat{{padding:30px;font-size:34px;color:#2B2A26;font-family:Georgia,serif}}
    .chat .you{{background:#EAE6DA;border-radius:22px;padding:22px;margin-left:60px;font-family:Pop}}
    .chat .ans{{margin-top:34px;line-height:1.35}}
    .chat .box{{position:absolute;left:30px;right:30px;bottom:30px;border:2px solid #DDD8CC;border-radius:24px;
               padding:22px;color:#8F8A7E;font-size:28px;background:#fff}}
    .me{{position:absolute;bottom:0;{me_css};width:{pw}px;filter:drop-shadow(0 0 28px rgba(0,0,0,.7))
         drop-shadow(0 0 3px {accent})}}
    .badge{{position:absolute;left:{badge_x}px;top:{badge_y}px;width:270px;height:270px;border-radius:50%;
            background:#FFD400;color:#0A0F1F;display:flex;flex-direction:column;align-items:center;
            justify-content:center;text-align:center;line-height:1;transform:rotate(-10deg);
            box-shadow:0 14px 40px rgba(0,0,0,.5);border:8px solid #fff}}
    .badge b{{font-weight:normal;font-size:{bsize}px}} .badge i{{font-style:normal;font-size:34px;margin-top:8px;
            letter-spacing:2px}}
    .arrow{{position:absolute;top:700px;width:220px;height:160px;filter:drop-shadow(0 4px 6px rgba(0,0,0,.6))}}
    </style></head><body><div class="g1"></div><div class="g2"></div><div class="grid"></div>
    <div class="tag">{tag}</div>
    <div class="title"><div id="t">{_title_html(text)}</div></div>
    <div class="screen"><div class="bar"><span class="dot"></span>{h.escape(label)}</div>{shot}</div>
    {me}{arrow if pose else ""}
    {f'<div class="badge"><b>{h.escape(bmain)}</b><i>{h.escape(bunit)}</i></div>' if badge else ""}
    <script>
      // shrink the title until it fits its box (max 3-4 lines, no word cut)
      const box = document.querySelector('.title'), t = document.getElementById('t');
      let s = 132;
      while (s > 60) {{
        box.style.fontSize = s + 'px';
        if (t.scrollHeight <= box.clientHeight && t.scrollWidth <= box.clientWidth) break;
        s -= 4;
      }}
    </script></body></html>"""
    hp = workdir / "cover.html"
    hp.write_text(page, encoding="utf-8")
    png, jpg = workdir / "cover.png", workdir / "cover.jpg"
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(hp.resolve().as_uri())
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(png))
        b.close()
    Image.open(png).convert("RGB").save(jpg, quality=88, optimize=True)
    print(f"[cover] '{text}'" + (f" + badge {badge}" if badge else "") + f", pose {(pose or {}).get('file')} ({side})")
    return png


def screen_for_cover(specs, shots):
    """The Short's best screen for the cover: a Claude chat first, then code / chain, else the first screen."""
    if not shots:
        return None
    order = {"claude": 0, "code": 1, "flow": 2, "api": 3}
    best = min(range(len(specs)), key=lambda i: (order.get(specs[i].get("app", ""), 9), i))
    return shots[best].get("plain")
