"""Vertical 9:16 Short from the long-video engine (15 Nov 2026) - no Flow, no Gemini: works every day.

  python -m longform.vshort build  docs/longform/shorts/<id>.json out/video out/<id>-short.mp4
  python -m longform.vshort upload docs/longform/shorts/<id>.json out/<id>-short.mp4   (-> out/uploaded.json)

The Short script is a normal longform script with "format": "short" (HOOK / CARTOON / BOARD / PODCAST scenes, ~30-55 s
spoken) plus: "kicker" (small label, e.g. "NEWS · 14 NOV 2026"), "headline" (big top text, *word* = yellow),
"source_line" ("Sources: ..."), "title", "description", "tags", "sources".
Render first (python -m longform.render ... --scale 1), then build: the 16:9 animation sits in the middle of a 1080x1920
frame with the headline on top, big word-group captions under it, the round presenter loop on the frame corner and the
source line at the bottom.
"""
import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
W, H = 1080, 1920
VY, VH = 610, 748          # where the animation sits (centre 1560x1080 of the 16:9 frame, scaled to 1080 wide)
CROP_W = 1560
SLOTS_IST = ["07:30", "13:30", "21:30"]   # Short publish times (IST); a slot is free if nothing else is within 40 min


def frame_png(sc, out):
    from playwright.sync_api import sync_playwright
    head = html.escape(sc.get("headline") or sc["title"]).replace("#Shorts", "")
    head = re.sub(r"\*(.+?)\*", r"<em>\1</em>", head)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Inter;src:url("{(ROOT / 'longform/fonts/Inter-Variable.ttf').as_uri()}");font-weight:100 900}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:Inter}}
body{{background:radial-gradient(900px 1100px at 50% 40%,#173a86 0%,#0f2a66 45%,#0a1838 100%);position:relative}}
.dots{{position:absolute;right:40px;top:120px;width:180px;height:100px;background-image:radial-gradient(#ffffff40 3px,transparent 3.5px);background-size:22px 22px}}
.brand{{position:absolute;left:60px;top:70px;display:flex;gap:14px;align-items:center;color:#fff;font-weight:800;font-size:34px}}
.brand i{{width:22px;height:22px;border-radius:6px;background:#0f9d8a;transform:rotate(45deg);display:inline-block}}
.kick{{position:absolute;left:60px;top:150px;background:#e4573d;color:#fff;font-weight:900;font-size:34px;padding:10px 22px;border-radius:12px;letter-spacing:1px}}
.head{{position:absolute;left:60px;right:60px;top:225px;height:350px;display:flex;align-items:center;color:#fff;font-weight:900;line-height:1.08;letter-spacing:-1px;font-size:84px}}
.head em{{font-style:normal;color:#ffd23f}}
.box{{position:absolute;left:0;top:{VY - 10}px;width:{W}px;height:{VH + 20}px;background:#f6f2eb}}
.src{{position:absolute;left:60px;right:60px;bottom:120px;color:#c9d4ee;font-weight:600;font-size:28px;line-height:1.3}}
</style></head><body><div class="dots"></div><div class="brand"><i></i>GSX Automation</div>
{f'<div class="kick">{html.escape(sc["kicker"])}</div>' if sc.get("kicker") else ''}
<div class="head" id="h"><span>{head}</span></div><div class="box"></div>
<div class="src">{html.escape(sc.get("source_line", ""))}</div>
<script>document.fonts.ready.then(()=>{{const h=document.getElementById('h');let f=84;while(h.firstChild.offsetHeight>340&&f>48){{f-=2;h.style.fontSize=f+'px';}}document.body.dataset.ready=1;}});</script>
</body></html>"""
    tmp = Path(out).with_suffix(".html")
    tmp.write_text(page)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(tmp.as_uri())
        pg.wait_for_selector("body[data-ready]", timeout=15000)
        pg.screenshot(path=str(out))
        b.close()


def groups(text, n=3):
    w, out, cur = text.split(), [], []
    for x in w:
        cur.append(x)
        if len(cur) >= n or re.search(r"[.,?!;:]$", x):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def ass(plan, out):
    from longform.render import cap_text

    def t(x):
        return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
    ev = []
    for s in plan:
        for c in s["cues"]:
            gs = groups(cap_text(c["text"]))
            tot = sum(len(g) for g in gs) or 1
            a = s["start"] + c["s"]
            for g in gs:
                d = (c["e"] - c["s"]) * len(g) / tot
                ev.append(f"Dialogue: 0,{t(a)},{t(a + d)},Cap,,0,0,0,,{g.upper()}")
                a += d
    Path(out).write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,86,&H0000D2FF,&H00FFFFFF,&H00101828,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,8,60,60,{VY + VH + 90},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")


def build(script, video_dir, out):
    from longform import corner as cn
    sc = json.loads(Path(script).read_text())
    vd = Path(video_dir)
    plan = json.loads((vd / "plan.json").read_text())
    src = vd / f"{sc['id']}.mp4"
    work = vd / "short"
    work.mkdir(exist_ok=True)
    frame_png(sc, work / "frame.png")
    ass(plan, work / "caps.ass")
    size = 210
    cmov = cn.build(work / f"corner_{size}.mov", size)
    fonts = ROOT / "longform/fonts"
    fc = (f"[1:v]crop={CROP_W}:1080:{(1920 - CROP_W) // 2}:0,scale={W}:{VH}:flags=lanczos,setsar=1[a];[0:v][a]overlay=0:{VY}:shortest=1[b];"
          f"[b][2:v]overlay={W - size - 40}:{VY - size // 2 - 20}:shortest=1[c];"
          f"[c]subtitles={work / 'caps.ass'}:fontsdir={fonts},format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(work / "frame.png"),
                    "-i", str(src), "-stream_loop", "-1", "-i", str(cmov), "-filter_complex", fc,
                    "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print(f"[vshort] {out}")


def pick_slot(yt, g):
    try:
        taken = [w for _, w in g.scheduled_times(yt, days_back=1)]
    except Exception as e:
        print(f"[vshort] could not read scheduled videos: {str(e)[:150]}")
        taken = []
    ist = dt.timezone(dt.timedelta(hours=5, minutes=30))
    now = dt.datetime.now(dt.timezone.utc)
    for day in range(0, 6):
        d = (now.astimezone(ist) + dt.timedelta(days=day)).date()
        for hm in SLOTS_IST:
            h, m = map(int, hm.split(":"))
            when = dt.datetime(d.year, d.month, d.day, h, m, tzinfo=ist).astimezone(dt.timezone.utc)
            if when < now + dt.timedelta(minutes=40):
                continue
            if all(abs((when - x).total_seconds()) > 40 * 60 for x in taken):
                return when
    return now + dt.timedelta(hours=1)


def upload(script, video):
    from autopilot import google_apis as g
    sc = json.loads(Path(script).read_text())
    yt = g.youtube()
    when = pick_slot(yt, g)
    pub = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    title = sc["title"].replace("<", "‹").replace(">", "›")
    if "#shorts" not in title.lower():
        title = (title[:90] + " #Shorts").strip()
    desc = sc["description"].replace("<", "‹").replace(">", "›")
    vid = g.upload(yt, video, title, desc, sc.get("tags", []), pub)
    print(f"[vshort] https://youtube.com/shorts/{vid}  public at {pub}")
    Path("out").mkdir(exist_ok=True)
    Path("out/uploaded.json").write_text(json.dumps({"video_id": vid, "publish_at": pub, "title": title}, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(*sys.argv[2:5])
    else:
        upload(*sys.argv[2:4])
