"""Builds the finished Short.

Two kinds of shots, cut together:
  * AVATAR shots (HOOK / PROBLEM / FIX / RESULT / CTA): YOU, full screen 9:16, the whole Flow frame is shown
    (body, hands, gestures, background) - no panel, no tight face crop. Only a very gentle camera move.
  * SCREEN shots (STEP n): the "card" layout -
      +--------------------------------+
      |  @channel . Zoho CRM + Claude  |   warm background, hook title on top
      |      BIG HOOK TITLE (2 lines)  |
      | +----------------------------+ |
      | | app / AI chat / API screen:| |   first the whole screen (so the viewer sees where we are),
      | | full view -> zoom to the   | |   then the camera zooms to the button / field to click,
      | | button / field             | |   timed to the end of the spoken line
      | +----------------------------+ |
      +--------------------------------+
Word-timed captions at the bottom for the whole video, soft background music ducked under the voice.
Every Short: the first ~1 s is the thumbnail cover (autopilot/thumbnail.py: caption + Gaurav + the Short's screen).
"""
import json
import random
import re
import subprocess
from pathlib import Path

from . import music, screens
from .config import CHANNEL_HANDLE, CHANNEL_NAME, IS_ZOHO

W, H, FPS = 1080, 1920, 30
PX, PY, PW, PH = 40, 470, 1000, 1100  # middle panel (screen shots)
CAP_Y = 1640  # caption centre (above the YouTube Shorts UI at the bottom)
BG, INK, ACCENT = "#F3ECE0", "#1E2433", "#2F6FEB"
AVATAR_ZOOMS = [1.0, 1.04, 1.0, 1.06]
MUSIC_VOL = 0.22 if IS_ZOHO else 0.34  # niche v2: QA said the music was hard to hear (still ducked under the voice)  # gentle variety between avatar cuts (never a tight face crop)


def _run(cmd):
    subprocess.run(cmd, check=True)


def _ff(*a):
    return ["ffmpeg", "-y", "-loglevel", "error", *a]


def _dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True, check=True).stdout.strip())


def _clean(t):
    return re.sub(r"\s+", " ", re.sub(r"[\[<][^\]>]{1,30}[\]>]", "", t or "")).strip()


# ------------------------------------------------------------------ timing
def line_times(lines, words, dur):
    """[(start, end)] per script line, from the script-aligned words (same order, same count)."""
    counts = [len(_clean(l.get("say") or l.get("tts")).split()) for l in lines]
    out, k = [], 0
    starts = []
    for c in counts:
        starts.append(words[k][0] if k < len(words) else (starts[-1] if starts else 0))
        k += c
    starts[0] = 0.0
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else dur
        out.append((s, max(e, s + 0.3)))
    return out


def _is_screen(line):
    """Lines spoken by the presenter on camera ("face", from Flow) show the presenter; every other line is a
    Zoho screen (its voice is TTS). Old jobs without the flag: only STEP lines with a screen spec."""
    if "face" in line:
        return not line["face"]
    beat = str(line.get("beat", "")).upper()
    return beat.startswith("STEP") and bool(line.get("screen"))


def _product_screen(spec, sc, line):
    """11 Nov 2026 (Gaurav): a Zoho Books Short showed Zoho Flow chains on every step. Every screen must be THE
    PRODUCT of the Short: a spec of another app (or a 'flow' chain in a non-Flow Short) is replaced by the product's
    best-matching REAL screenshot (assets/screens), else by the product's own drawn app page."""
    if not IS_ZOHO or not spec:
        return spec
    label = str(sc.get("app_label") or "").lower()
    prod = next((a for a in ("books", "crm", "campaigns", "analytics", "desk", "creator", "inventory", "people",
                             "salesiq", "social", "sign", "flow", "bigin", "one") if a in label), "")
    app = str(spec.get("app") or "").lower().replace("zoho ", "")
    view = str(spec.get("view") or "").lower()
    if not prod or prod == "flow" or app in ("claude", "chatgpt", "api", "code", "presenter") or spec.get("real"):
        return spec
    if app == prod and view != "flow":
        return spec
    lib = screens.library()
    words = set(re.findall(r"[a-z]{4,}", (line.get("say", "") + " " + line.get("card", "")).lower()))
    best, score = None, 0
    for key, v in lib.items():
        if not key.startswith(prod + "/"):
            continue
        sc_ = len(words & set(re.findall(r"[a-z]{4,}", (key + " " + str(v.get("about", ""))).lower())))
        if sc_ > score:
            best, score = key, sc_
    if best:
        print(f"[screens] '{line.get('beat')}': {app or '?'}/{view or '?'} screen in a {prod} Short -> real {best}")
        return {"real": best, "app": prod, "click": "", "tip": spec.get("tip", "")}
    print(f"[screens] '{line.get('beat')}': {app or '?'}/{view or '?'} screen in a {prod} Short -> {prod} app page")
    return {"app": prod, "view": "settings", "path": [line.get("card") or "Settings"], "tip": spec.get("tip", "")}


def _spec_for(lines, i):
    """The line's own screen spec, else the next one's (FIX usually leads into STEP 1), else the previous one."""
    if lines[i].get("screen"):
        return lines[i]["screen"]
    order = list(range(i + 1, len(lines))) + list(range(i - 1, -1, -1))
    return next((lines[j]["screen"] for j in order if lines[j].get("screen")), None)


def plan(lines, times, dur):
    """Visual segments: [{"kind": "avatar"|"screen", "t0", "t1", "line": i, "zoom": z}]"""
    segs = []
    for i, (l, (a, b)) in enumerate(zip(lines, times)):
        kind = "screen" if _is_screen(l) else "avatar"
        if segs and kind == "avatar" and segs[-1]["kind"] == "avatar":
            segs[-1]["t1"] = b
        else:
            segs.append({"kind": kind, "t0": a, "t1": b, "line": i})
    segs[-1]["t1"] = dur
    return _soft_cuts(segs)


def _soft_cuts(segs):
    """Long avatar shots -> soft cuts (tiny zoom change) every ~4 s."""
    out = []
    for s in segs:
        if s["kind"] == "avatar" and s["t1"] - s["t0"] > 4.5:
            n = max(2, round((s["t1"] - s["t0"]) / 4.0))
            step = (s["t1"] - s["t0"]) / n
            for j in range(n):
                out.append(s | {"t0": s["t0"] + j * step, "t1": s["t0"] + (j + 1) * step,
                                "zoom": AVATAR_ZOOMS[j % len(AVATAR_ZOOMS)]})
        else:
            out.append(s | {"zoom": 1.0})
    return out


def plan_parts(timeline, dur):
    """Visual segments from the EXACT lengths of the parts the assembler joined: [(kind, line, seconds)].
    Word timings from whisper can be off by a second or more; part lengths cannot. So the presenter is shown
    only where his Flow clip really is and a Zoho screen exactly where a TTS line is - the black placeholder
    under the screen parts can never leak into the video (that was the 3-5 s black screen)."""
    segs, t = [], 0.0
    for kind, li, ln in timeline:
        if segs and segs[-1]["kind"] == kind and (kind == "avatar" or segs[-1]["line"] == li):
            segs[-1]["t1"] = t + ln
        else:
            segs.append({"kind": kind, "t0": t, "t1": t + ln, "line": li})
        t += ln
    if segs:
        segs[-1]["t1"] = max(dur, segs[-1]["t0"] + 0.1)
    return _soft_cuts(segs)


# ------------------------------------------------------------------ clips
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def _avatar_full(av, t0, frames, zoom, out):
    """The presenter full screen 9:16 - the whole frame, scaled to fit (blurred fill if the clip is not 9:16)."""
    zw, zh = int(W * zoom) // 2 * 2, int(H * zoom) // 2 * 2
    fc = (f"[0:v]tpad=stop_mode=clone:stop_duration=10,fps={FPS},split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,setsar=1[bg];"
          f"[b]scale={zw}:{zh}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg0];"
          f"[bg][fg0]overlay=(W-w)/2:(H-h)*0.35,crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.35,setsar=1[v]")
    if not IS_ZOHO:  # niche v3: Veo sometimes burns garbled subtitles into the bottom of the clip (1 Nov: "500s$000
        # Cladess a morth"). A dark lower band (our captions sit on it) covers that area on every presenter shot.
        band = _lower_band(Path(out).parent)
        fc = fc.replace(",setsar=1[v]", ",setsar=1[v0];[v0][1:v]overlay=0:0[v]")
        _run(_ff("-ss", f"{t0:.3f}", "-i", str(av), "-loop", "1", "-i", str(band), "-filter_complex", fc,
                 "-map", "[v]", "-frames:v", str(frames), *ENC, str(out)))
        return
    _run(_ff("-ss", f"{t0:.3f}", "-i", str(av), "-filter_complex", fc, "-map", "[v]",
             "-frames:v", str(frames), *ENC, str(out)))


def _lower_band(workdir: Path):
    """Full-frame PNG: transparent on top, a soft fade into near-black over the bottom ~27% of the frame."""
    from PIL import Image
    png = Path(workdir) / "lower_band.png"
    if png.exists():
        return png
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top, solid = int(H * 0.68), int(H * 0.79)  # fade 68-79 %, fully solid below (Veo's subtitle zone is ~80-93 %)
    px = im.load()
    for y in range(top, H):
        a = 255 if y >= solid else int(255 * (y - top) / max(solid - top, 1))
        for x in range(W):
            px[x, y] = (8, 10, 22, a)
    im.save(png)
    return png


def _still_clip(png, frames, out, z0=1.0, z1=1.04, cx=None, cy=None, reach=0.7):
    """Ken-Burns on a 2x screen PNG; (cx, cy) = zoom target in 1x panel pixels; the zoom arrives at `reach`."""
    cx = PW / 2 if cx is None else cx
    cy = PH / 2 if cy is None else cy
    n = max(frames, 2)
    p = f"min(on/{n * reach:.1f},1)"
    ease = f"(1-pow(1-{p},3))"
    z = f"{z0}+({z1}-{z0})*{ease}"
    S = 4  # work at 4x to avoid zoompan jitter
    X = f"max(0,min(iw-iw/zoom,({PW / 2}+({cx}-{PW / 2})*{ease})*{S}-iw/zoom/2))"
    Y = f"max(0,min(ih-ih/zoom,({PH / 2}+({cy}-{PH / 2})*{ease})*{S}-ih/zoom/2))"
    vf = (f"scale={PW * S}:{PH * S},zoompan=z='{z}':x='{X}':y='{Y}':d={n}:s={PW}x{PH}:fps={FPS},setsar=1")
    _run(_ff("-loop", "1", "-i", str(png), "-vf", vf, "-frames:v", str(frames), *ENC, str(out)))


def _card(panel_mp4, bg, fg, frames, out):
    """Screen panel -> full 1080x1920 card frame (title on top, panel in the middle)."""
    fc = f"[0:v][1:v]overlay={PX}:{PY}:shortest=1[a];[a][2:v]overlay=0:{PY - 40},setsar=1[v]"
    _run(_ff("-loop", "1", "-i", str(bg), "-i", str(panel_mp4), "-loop", "1", "-i", str(fg),
             "-filter_complex", fc, "-map", "[v]", "-frames:v", str(frames), *ENC, str(out)))


# ------------------------------------------------------------------ static layers
def _app_label(sc, specs):
    """Top tag text: the script's own label ("Zoho CRM + Claude"), else from the first screen's app."""
    if not IS_ZOHO:  # niche switch - below is the Zoho niche, unchanged
        from .niche_claude_wealth import app_label
        return app_label(sc, specs)
    import html as h
    lab = str(sc.get("app_label") or "").strip()
    if not lab and specs:
        app = specs[0].get("app", "")
        lab = {"claude": "Claude + Zoho", "chatgpt": "ChatGPT + Zoho", "api": "Zoho API", "code": "Zoho dev",
               "flow": "Zoho Flow"}.get(app) or (f"Zoho {screens.APPS[app]['name']}" if app in screens.APPS else "Zoho")
    return h.escape(lab[:28] or "Zoho")


def _layers(hook, workdir: Path, app_label="Zoho"):
    from playwright.sync_api import sync_playwright
    hook = (hook or "").strip()
    size = 78 if len(hook) <= 22 else 66 if len(hook) <= 34 else 56
    tag = f"@{CHANNEL_HANDLE.lstrip('@')}" if CHANNEL_HANDLE else CHANNEL_NAME
    bg_html = f"""<html><head><meta charset="utf-8"><style>
    body{{margin:0;width:{W}px;height:{H}px;background:{BG};font-family:'Noto Sans','Inter',sans-serif;overflow:hidden}}
    .dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(30,36,51,.06) 2px,transparent 2px);
           background-size:34px 34px}}
    .tag{{position:absolute;top:120px;left:0;right:0;text-align:center}}
    .tag span{{display:inline-block;background:{INK};color:#fff;font-weight:700;font-size:30px;padding:10px 24px;
              border-radius:40px;letter-spacing:.5px}}
    .tag b{{color:#FFC93C}}
    .title{{position:absolute;top:196px;left:60px;right:60px;height:250px;display:flex;align-items:center;
            justify-content:center;text-align:center;font-weight:900;font-size:{size}px;line-height:1.08;color:{INK}}}
    .title em{{font-style:normal;color:{ACCENT}}}
    .shadow{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PH}px;border-radius:36px;
             box-shadow:0 18px 50px rgba(30,36,51,.28);background:#000}}
    </style></head><body><div class="dots"></div>
    <div class="tag"><span>{tag} · <b>{app_label}</b></span></div>
    <div class="title"><div>{_title_html(hook)}</div></div><div class="shadow"></div></body></html>"""
    fg_html = f"""<html><head><style>body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden}}
    .hole{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PH}px;border-radius:36px;
           box-shadow:0 0 0 2000px {BG};outline:6px solid #fff;outline-offset:-3px}}</style></head>
    <body><div class="hole"></div></body></html>"""
    bg, fg = workdir / "bg.png", workdir / "fg.png"
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(bg_html)
        pg.screenshot(path=str(bg))
        pg.set_content(fg_html)
        pg.screenshot(path=str(fg), omit_background=True, clip={"x": 0, "y": PY - 40, "width": W, "height": PH + 80})
        b.close()
    return bg, fg


def _layers_v2(hook, workdir: Path, app_label, sc):
    """Claude niche v2 (1 Nov 2026): deep navy card with soft glows in the industry's colour, a fine grid, the
    industry name + tool in the top tag, white hook title. Same geometry as _layers (panel at PX, PY), so the
    screen panel, zoom and captions work exactly the same."""
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw
    from .niche_claude_wealth import accent_for, industry_name
    import html as h
    acc = accent_for(sc)
    ind = h.escape(industry_name(sc).upper())
    hook = (hook or "").strip()
    size = 78 if len(hook) <= 22 else 66 if len(hook) <= 34 else 56
    tag = f"@{CHANNEL_HANDLE.lstrip('@')}" if CHANNEL_HANDLE else CHANNEL_NAME
    chip = f'<div class="ind">{ind}</div>' if ind else ""
    bg_html = f"""<html><head><meta charset="utf-8"><style>
    body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:'Noto Sans','Inter',sans-serif;
         background:linear-gradient(165deg,#0B1020 0%,#121A33 55%,#0B1020 100%)}}
    .g1{{position:absolute;width:900px;height:900px;left:-260px;top:-300px;border-radius:50%;
         background:radial-gradient(circle,{acc}66 0%,transparent 65%)}}
    .g2{{position:absolute;width:1000px;height:1000px;right:-380px;bottom:-360px;border-radius:50%;
         background:radial-gradient(circle,{acc}40 0%,transparent 62%)}}
    .grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
           linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:60px 60px}}
    .ind{{position:absolute;top:58px;left:0;right:0;text-align:center;color:{acc};font-weight:800;font-size:28px;
          letter-spacing:6px}}
    .tag{{position:absolute;top:110px;left:0;right:0;text-align:center}}
    .tag span{{display:inline-block;background:rgba(255,255,255,.10);border:2px solid rgba(255,255,255,.18);
              color:#fff;font-weight:700;font-size:30px;padding:10px 26px;border-radius:40px;letter-spacing:.5px}}
    .tag b{{color:#FFC93C}}
    .title{{position:absolute;top:196px;left:60px;right:60px;height:250px;display:flex;align-items:center;
            justify-content:center;text-align:center;font-weight:900;font-size:{size}px;line-height:1.08;color:#fff;
            text-shadow:0 6px 24px rgba(0,0,0,.45)}}
    .title em{{font-style:normal;color:{acc}}}
    .shadow{{position:absolute;left:{PX}px;top:{PY}px;width:{PW}px;height:{PH}px;border-radius:36px;
             box-shadow:0 0 0 3px {acc}AA,0 24px 70px rgba(0,0,0,.6),0 0 90px {acc}55;background:#000}}
    </style></head><body><div class="g1"></div><div class="g2"></div><div class="grid"></div>{chip}
    <div class="tag"><span>{tag} · <b>{app_label}</b></span></div>
    <div class="title"><div>{_title_html(hook)}</div></div><div class="shadow"></div></body></html>"""
    bg, fg = workdir / "bg.png", workdir / "fg.png"
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(bg_html)
        pg.screenshot(path=str(bg))
        b.close()
    # foreground = the same background with a rounded hole where the panel is (+ a thin white frame), so the
    # panel's corners are rounded on the gradient too (a flat colour mask would show as a band here)
    top = PY - 40
    over = Image.open(bg).convert("RGBA").crop((0, top, W, top + PH + 80))
    mask = Image.new("L", over.size, 255)
    ImageDraw.Draw(mask).rounded_rectangle((PX, 40, PX + PW - 1, 40 + PH - 1), radius=36, fill=0)
    over.putalpha(mask)
    ImageDraw.Draw(over).rounded_rectangle((PX, 40, PX + PW - 1, 40 + PH - 1), radius=36,
                                           outline=(255, 255, 255, 235), width=5)
    over.save(fg)
    return bg, fg


def _cover(sc, specs, shots, workdir: Path):
    """Thumbnail cover (autopilot/thumbnail.py): the first ~1 s of the Short = Gaurav's photo + the news / problem as a
    big caption + the Short's own screen. 10 Nov 2026: on for the Zoho niche too (Gaurav: every Short opens on it).
    A cover problem never blocks a Short: it is then simply built without the cover, as before."""
    try:
        from . import thumbnail
        if IS_ZOHO:
            app = str(sc.get("app_label") or "Zoho")
            accent = _ZOHO_ACCENT.get(next((k for k in _ZOHO_ACCENT if k in app.lower()), ""), "#E42527")
            return thumbnail.cover(sc, workdir, thumbnail.screen_for_cover(specs, shots), accent=accent,
                                   handle=CHANNEL_HANDLE, label=app[:32])
        from .niche_claude_wealth import accent_for
        return thumbnail.cover(sc, workdir, thumbnail.screen_for_cover(specs, shots), accent=accent_for(sc),
                               handle=CHANNEL_HANDLE, label="Claude")
    except Exception as e:
        print(f"[cover] skipped: {str(e)[:200]}")
        return None


# cover glow colour per Zoho product (else Zoho red)
_ZOHO_ACCENT = {"crm": "#E42527", "books": "#2E7D32", "analytics": "#1E88E5", "campaigns": "#F57C00",
                "desk": "#00897B", "flow": "#7E57C2", "creator": "#C2185B", "social": "#0288D1",
                "salesiq": "#FF7043", "sign": "#3949AB", "inventory": "#6D4C41", "people": "#00ACC1"}


def _title_html(hook):
    import html as h
    ws = hook.split()
    if not ws:
        return ""
    # colour the last 1-2 words (the "pain" word usually sits at the end)
    k = 2 if len(ws) >= 4 else 1
    return h.escape(" ".join(ws[:-k])) + " <em>" + h.escape(" ".join(ws[-k:])) + "</em>"


# ------------------------------------------------------------------ captions
def _ts(t):
    t = max(t, 0)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _e(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")")


def _chunks(words, line_ends, max_words=4, max_chars=22):
    out, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or len(" ".join(x[2] for x in cur + [w])) > max_chars
                    or any(cur[-1][1] <= e < w[1] for e in line_ends) or re.search(r"[.?!,।]$", cur[-1][2])):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def build_ass(words, lines, times, segs, path, hook=""):
    yellow, white = r"{\c&H003CC9FF&}", r"{\c&H00FFFFFF&}"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Noto Sans,64,&H00FFFFFF,&H00FFFFFF,&H00332B1E,&H64000000,1,0,0,0,100,100,0,0,3,18,0,5,40,40,0,1
Style: Chip,Noto Sans,40,&H00FFFFFF,&H00FFFFFF,&H00EB6F2F,&H00000000,1,0,0,0,100,100,1,0,3,12,0,7,0,0,0,1
Style: Hook,Noto Sans,70,&H00FFFFFF,&H00FFFFFF,&H00332B1E,&H64000000,1,0,0,0,100,100,0,0,3,20,0,8,60,60,190,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    ends = [b for _, b in times]
    chs = _chunks(words, ends)
    for ci, ch in enumerate(chs):
        txt = [_e(w[2]) for w in ch]
        nxt = chs[ci + 1][0][0] if ci + 1 < len(chs) else 1e9
        for j, w in enumerate(ch):
            s = w[0] if j else ch[0][0]
            e = ch[j + 1][0] if j + 1 < len(ch) else min(w[1] + 0.25, nxt)
            body = " ".join((yellow + t + white) if k == j else t for k, t in enumerate(txt))
            ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},Cap,,0,0,0,,{{\\pos({W // 2},{CAP_Y})}}{body}")
    # hook title on top of the first presenter shot (the card layout has its own title)
    if hook and segs and segs[0]["kind"] == "avatar":
        ev.append(f"Dialogue: 2,{_ts(0)},{_ts(min(segs[0]['t1'], 3.2))},Hook,,0,0,0,,"
                  f"{{\\fad(120,200)}}{_e(hook.upper())}")
    for s in segs:  # "STEP 2" chip on screen shots
        if s["kind"] == "screen":
            beat = str(lines[s["line"]].get("beat", "")).upper()
            label = beat if beat.startswith("STEP") else "HOW TO FIX" if beat.startswith("FIX") else beat
            if not IS_ZOHO:  # niche v3 money format
                label = {"SELL": "WHAT TO SELL", "CLIENTS": "FIRST CLIENT", "MATH": "THE MONEY", "RESULT": "THE CATCH",
                         "FIX": "HOW", "PROBLEM": "WHY IT PAYS"}.get(beat.split(" ")[0], label)
            if not IS_ZOHO and beat.startswith("HOOK"):
                continue  # faceless hook card: no chip
            ev.append(f"Dialogue: 2,{_ts(s['t0'])},{_ts(s['t1'])},Chip,,0,0,0,,{{\\pos({PX + 28},{PY + PH - 92})}} {_e(label)} ")
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main
def render(sc, lines, words, avatar_mp4, voice_wav, workdir: Path, out_path: Path, seed=None, timeline=None):
    workdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    dur = _dur(voice_wav)
    times = line_times(lines, words, dur)
    segs = plan_parts(timeline, dur) if timeline else plan(lines, times, dur)

    specs, idx = [], {}
    for s in segs:
        if s["kind"] == "screen":
            l = lines[s["line"]]
            idx[s["line"]] = len(specs)
            spec = _product_screen(_spec_for(lines, s["line"]), sc, l)
            if IS_ZOHO and not l.get("screen") and str(l.get("beat", "")).upper().startswith(("HOOK", "PROBLEM", "RESULT")):
                # 10 Nov 2026: faceless Zoho Short -> Gaurav's photo card with the line's caption (no Flow clip here)
                app = str(sc.get("app_label") or "")
                spec = {"app": "presenter", "text": l.get("card") or l.get("say", "")[:60], "seed": sc.get("title", ""),
                        "accent": _ZOHO_ACCENT.get(next((k for k in _ZOHO_ACCENT if k in app.lower()), ""), "#E42527")}
            specs.append(screens.normalize(spec, l.get("card", ""), l.get("beat", "")))
    shots = screens.render(specs, workdir / "screens") if specs else []
    hook = sc.get("hook_text") or sc.get("title", "")
    bg = fg = None
    if specs:
        if IS_ZOHO:  # the Zoho niche, unchanged
            bg, fg = _layers(hook, workdir, _app_label(sc, specs))
        else:  # niche v2: dark, professional card coloured by the Short's industry
            bg, fg = _layers_v2(hook, workdir, _app_label(sc, specs), sc)

    clips, fb = [], [round(s["t0"] * FPS) for s in segs] + [round(dur * FPS)]
    for k, s in enumerate(segs):
        frames = max(fb[k + 1] - fb[k], 1)
        if s["kind"] == "avatar":
            c = workdir / f"c{k:02d}.mp4"
            _avatar_full(avatar_mp4, s["t0"], frames, s["zoom"], c)
            clips.append(c)
            continue
        sh = shots[idx[s["line"]]]
        x, y, w, h = sh["box"]
        cx, cy = x + w / 2, y + h / 2
        z1 = max(1.4, min(1.8, PW / (2.4 * max(w, 60))))
        fa = min(max(int(frames * 0.45), int(0.6 * FPS)), int(2.4 * FPS)) if frames > 30 else 0
        if not IS_ZOHO:  # niche v2 (1.5x pace = short lines): gentle zoom so no text is cut off at the edges, and
            z1 = 1.04    # v3: almost no zoom - the whole screen stays readable, nothing cut off
            fa = min(max(int(frames * 0.55), int(0.6 * FPS)), int(2.6 * FPS)) if frames > 30 else 0
        # first show the WHOLE screen (where are we?), then zoom to the click near the end of the spoken line
        parts = []
        if fa:
            a = workdir / f"p{k:02d}a.mp4"
            _still_clip(sh["plain"], fa, a, 1.0, 1.02)
            parts.append(a)
        b = workdir / f"p{k:02d}b.mp4"
        _still_clip(sh["hl"], frames - fa, b, 1.02 if fa else 1.0, z1, cx, cy, reach=0.6)
        parts.append(b)
        pl = workdir / f"p{k:02d}.txt"
        pl.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        panel = workdir / f"p{k:02d}.mp4"
        _run(_ff("-f", "concat", "-safe", "0", "-i", str(pl), "-c", "copy", str(panel)))
        c = workdir / f"c{k:02d}.mp4"
        _card(panel, bg, fg, frames, c)
        clips.append(c)

    lst = workdir / "clips.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    video = workdir / "video.mp4"
    _run(_ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(video)))
    # editor's self-check before captions + music go on top: not one black frame may reach YouTube
    from .editor import black_spans
    black = black_spans(video)
    if black:
        raise RuntimeError("black frames in the edit at " + ", ".join(f"{a:.1f}-{b:.1f}s" for a, b in black[:5])
                           + " - a screen / presenter shot is missing there; not uploading a broken Short")

    ass = workdir / "captions.ass"
    build_ass(words, lines, times, segs, ass, hook)
    mus = music.pick(dur + 1, workdir, seed)
    ass_arg = str(ass.resolve()).replace(":", r"\:").replace("'", r"\'")
    cover = _cover(sc, specs, shots, workdir)
    cin, cfc = [], ""
    if cover:  # 2 Nov 2026: the Short OPENS on its thumbnail (title + Gaurav + Claude screen) - that first frame is
        # what the Shorts feed / channel grid shows. ~1 s with a gentle push-in (never a frozen frame), the hook voice
        # already plays under it, then it fades into the Short. Video length / voice sync do not change.
        from .thumbnail import INTRO
        n = int(INTRO * FPS)
        cin = ["-loop", "1", "-framerate", str(FPS), "-t", f"{INTRO:.2f}", "-i", str(cover)]
        cfc = (f"[3:v]scale={W * 2}:{H * 2},zoompan=z='1+0.045*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:"
               f"s={W}x{H}:fps={FPS},format=yuva420p,fade=t=out:st={INTRO - 0.2:.2f}:d=0.2:alpha=1[cv];"
               f"[vc][cv]overlay=0:0:eof_action=pass[v];")
    fc = (f"[0:v]ass='{ass_arg}'[{'vc' if cover else 'v'}];{cfc}"
          f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={MUSIC_VOL:.2f}[m];"
          f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[vo][sc];"
          f"[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
          f"[vo][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]")
    _run(_ff("-i", str(video), "-i", str(voice_wav), "-stream_loop", "-1", "-i", str(mus), *cin,
             "-filter_complex", fc, "-map", "[v]", "-map", "[aout]",
             "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
             "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)))
    (workdir / "plan.json").write_text(json.dumps(
        [{k: v for k, v in s.items()} | {"beat": lines[s["line"]].get("beat")} for s in segs], indent=1))
    print(f"[composer] {len(segs)} shots ({sum(s['kind'] == 'screen' for s in segs)} screens), "
          f"{dur:.1f}s -> {out_path}")
    return out_path
