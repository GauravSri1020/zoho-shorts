"""Builds the finished Short (layout inspired by the reference videos in channel.yaml -> benchmark):

  +--------------------------------+
  |  @channel  ·  Zoho Books tip   |   warm background, big hook title on top for the whole video
  |  BIG HOOK TITLE (2 lines)      |
  | +----------------------------+ |
  | |  middle panel switches:    | |   HOOK / PROBLEM / RESULT / CTA -> your talking (lip-synced) avatar
  | |  avatar  <->  Zoho screen  | |   FIX / STEP n                  -> Zoho Books screen, camera zooms to
  | |                            | |                                    the button / field to click
  | +----------------------------+ |
  |   [ caption box, word-timed ]  |
  +--------------------------------+
Hard cuts every ~3 s (punch-in on the avatar), soft background music ducked under the voice.
"""
import json
import random
import re
import subprocess
from pathlib import Path

from . import music, screens
from .config import CHANNEL_HANDLE, CHANNEL_NAME

W, H, FPS = 1080, 1920, 30
PX, PY, PW, PH = 40, 470, 1000, 1100           # middle panel
CAP_Y = 1685
BG, INK, ACCENT = "#F3ECE0", "#1E2433", "#2F6FEB"


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
    beat = str(line.get("beat", "")).upper()
    if line.get("screen"):
        return not beat.startswith(("HOOK", "CTA"))
    return beat.startswith("STEP") or (beat.startswith("FIX") and ">" in str(line.get("card", "")))


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
    out = []
    for s in segs:                                   # avatar shots longer than ~3.5 s -> punch-in cuts
        if s["kind"] == "avatar" and s["t1"] - s["t0"] > 3.6:
            n = max(2, round((s["t1"] - s["t0"]) / 3.0))
            step = (s["t1"] - s["t0"]) / n
            for j in range(n):
                out.append(s | {"t0": s["t0"] + j * step, "t1": s["t0"] + (j + 1) * step,
                                "zoom": [1.0, 1.18, 1.06, 1.25][j % 4]})
        else:
            out.append(s | {"zoom": 1.0})
    return out


# ------------------------------------------------------------------ clips
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


def _avatar_clip(av, t0, frames, zoom, out):
    zw, zh = int(PW * zoom) // 2 * 2, int(PH * zoom) // 2 * 2
    vf = (f"tpad=stop_mode=clone:stop_duration=10,fps={FPS},"
          f"scale={zw}:{zh}:force_original_aspect_ratio=increase,"
          f"crop={PW}:{PH}:(iw-{PW})/2:(ih-{PH})*0.22,setsar=1")
    _run(_ff("-ss", f"{t0:.3f}", "-i", str(av), "-vf", vf, "-frames:v", str(frames), *ENC, str(out)))


def _still_clip(png, frames, out, z0=1.0, z1=1.04, cx=None, cy=None):
    """Ken-Burns on a 2x screen PNG; (cx, cy) = zoom target in 1x panel pixels."""
    cx = PW / 2 if cx is None else cx
    cy = PH / 2 if cy is None else cy
    n = max(frames, 2)
    p = f"min(on/{n * 0.55:.1f},1)"
    ease = f"(1-pow(1-{p},3))"
    z = f"{z0}+({z1}-{z0})*{ease}"
    S = 4                                             # work at 4x to avoid zoompan jitter
    X = f"max(0,min(iw-iw/zoom,({PW / 2}+({cx}-{PW / 2})*{ease})*{S}-iw/zoom/2))"
    Y = f"max(0,min(ih-ih/zoom,({PH / 2}+({cy}-{PH / 2})*{ease})*{S}-ih/zoom/2))"
    vf = (f"scale={PW * S}:{PH * S},zoompan=z='{z}':x='{X}':y='{Y}':d={n}:s={PW}x{PH}:fps={FPS},setsar=1")
    _run(_ff("-loop", "1", "-i", str(png), "-vf", vf, "-frames:v", str(frames), *ENC, str(out)))


# ------------------------------------------------------------------ static layers
def _layers(hook, workdir: Path):
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
    <div class="tag"><span>{tag} · <b>Zoho Books</b> tip</span></div>
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


def build_ass(words, lines, times, segs, path):
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
    for s in segs:                                    # "STEP 2" chip on screen shots
        if s["kind"] == "screen":
            beat = str(lines[s["line"]].get("beat", "")).upper()
            label = beat if beat.startswith("STEP") else "HOW TO FIX" if beat.startswith("FIX") else beat
            ev.append(f"Dialogue: 2,{_ts(s['t0'])},{_ts(s['t1'])},Chip,,0,0,0,,{{\\pos({PX + 28},{PY + PH - 92})}} {_e(label)} ")
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main
def render(sc, lines, words, avatar_mp4, voice_wav, workdir: Path, out_path: Path, seed=None):
    workdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    dur = _dur(voice_wav)
    times = line_times(lines, words, dur)
    segs = plan(lines, times, dur)

    specs, idx = [], {}
    for s in segs:
        if s["kind"] == "screen":
            l = lines[s["line"]]
            idx[s["line"]] = len(specs)
            specs.append(screens.normalize(l.get("screen"), l.get("card", ""), l.get("beat", "")))
    shots = screens.render(specs, workdir / "screens") if specs else []

    clips, fb = [], [round(s["t0"] * FPS) for s in segs] + [round(dur * FPS)]
    for k, s in enumerate(segs):
        frames = max(fb[k + 1] - fb[k], 1)
        if s["kind"] == "avatar":
            c = workdir / f"c{k:02d}.mp4"
            _avatar_clip(avatar_mp4, s["t0"], frames, s["zoom"], c)
            clips.append(c)
        else:
            sh = shots[idx[s["line"]]]
            x, y, w, h = sh["box"]
            cx, cy = x + w / 2, y + h / 2
            z1 = max(1.45, min(1.9, PW / (2.4 * max(w, 60))))
            fa = min(max(int(frames * 0.3), 1), int(1.1 * FPS)) if frames > 20 else 0
            if fa:
                a = workdir / f"c{k:02d}a.mp4"
                _still_clip(sh["plain"], fa, a, 1.0, 1.03)
                clips.append(a)
            b = workdir / f"c{k:02d}b.mp4"
            _still_clip(sh["hl"], frames - fa, b, 1.03 if fa else 1.0, z1, cx, cy)
            clips.append(b)
    lst = workdir / "clips.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    panel = workdir / "panel.mp4"
    _run(_ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(panel)))

    bg, fg = _layers(sc.get("hook_text") or sc.get("title", ""), workdir)
    ass = workdir / "captions.ass"
    build_ass(words, lines, times, segs, ass)
    mus = music.pick(dur + 1, workdir, seed)
    ass_arg = str(ass.resolve()).replace(":", r"\:").replace("'", r"\'")
    fc = (f"[0:v][1:v]overlay={PX}:{PY}:shortest=1[a];[a][2:v]overlay=0:{PY - 40}[b];[b]ass='{ass_arg}'[v];"
          f"[4:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.22[m];"
          f"[3:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[vo][sc];"
          f"[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
          f"[vo][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]")
    _run(_ff("-loop", "1", "-i", str(bg), "-i", str(panel), "-loop", "1", "-i", str(fg), "-i", str(voice_wav),
             "-stream_loop", "-1", "-i", str(mus), "-filter_complex", fc, "-map", "[v]", "-map", "[aout]",
             "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
             "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)))
    (workdir / "plan.json").write_text(json.dumps(
        [{k: v for k, v in s.items()} | {"beat": lines[s["line"]].get("beat")} for s in segs], indent=1))
    print(f"[composer] {len(segs)} shots ({sum(s['kind'] == 'screen' for s in segs)} Zoho screens), "
          f"{dur:.1f}s -> {out_path}")
    return out_path
