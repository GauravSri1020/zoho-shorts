"""Animated whiteboard panels for steps that have no real Zoho screenshot (23 Nov 2026).

Gaurav: "beech mein wo screen aa rahi hai gandi si, jo stuck hai" - the old presenter card was ONE still photo + text.
Rule now: when the face goes away, the viewer sees either a real Zoho screen with a click, or a MOVING whiteboard
scene. This module draws that scene frame by frame (Playwright, like the long-video renderer) at panel size:

  marker-drawn icon (SVG stroke animation, a marker pen follows the line) -> STEP chip -> the card text pops in
  word by word -> the menu path / detail appears as pills one by one -> a green check draws itself at the end.

Nothing in the frame is ever still for more than ~0.4 s (QA's freeze check would fail it).
"""
import html as _h
import json
import re
import subprocess
from pathlib import Path

ICONS = {  # 300x300 viewBox, drawn as marker strokes
    "key": ["M95 150 a55 55 0 1 0 0.1 0", "M150 150 L265 150", "M225 150 L225 190", "M255 150 L255 180"],
    "ticket": ["M50 95 L250 95 L250 130 a20 20 0 0 0 0 40 L250 205 L50 205 L50 170 a20 20 0 0 0 0 -40 Z",
               "M110 95 L110 205", "M140 130 L220 130", "M140 170 L200 170"],
    "branch": ["M150 40 L150 120", "M150 120 L70 200", "M150 120 L150 200", "M150 120 L230 200",
               "M120 25 L180 25 L180 55 L120 55 Z", "M45 205 L95 205 L95 250 L45 250 Z",
               "M125 205 L175 205 L175 250 L125 250 Z", "M205 205 L255 205 L255 250 L205 250 Z"],
    "clock": ["M150 50 a100 100 0 1 0 0.1 0", "M150 150 L150 90", "M150 150 L200 175"],
    "building": ["M40 260 L260 260", "M60 120 L240 120 L150 55 Z", "M80 130 L80 245", "M125 130 L125 245",
                 "M175 130 L175 245", "M220 130 L220 245"],
    "shield": ["M150 35 L250 75 C250 170 210 230 150 265 C90 230 50 170 50 75 Z", "M105 150 L140 185 L200 115"],
    "invoice": ["M75 35 L195 35 L235 75 L235 265 L75 265 Z", "M195 35 L195 75 L235 75", "M105 120 L205 120",
                "M105 160 L205 160", "M105 200 L170 200"],
    "gear": ["M150 95 a55 55 0 1 0 0.1 0", "M150 30 L150 70", "M150 230 L150 270", "M30 150 L70 150",
             "M230 150 L270 150", "M65 65 L93 93", "M207 207 L235 235", "M235 65 L207 93", "M93 207 L65 235"],
    "chart": ["M50 255 L260 255", "M50 255 L50 45", "M80 220 L130 160 L170 190 L240 90", "M210 90 L240 90 L240 120"],
    "rocket": ["M150 30 C205 75 215 160 185 215 L115 215 C85 160 95 75 150 30 Z", "M150 105 a18 18 0 1 0 0.1 0",
               "M115 185 L80 230 L120 220", "M185 185 L220 230 L180 220", "M135 235 L150 270 L165 235"],
}
KEYWORDS = [  # first match wins
    ("key", r"access|request|unlock|permission|login|sign in"),
    ("building", r"emaratax|fta|ministry|government|authority|zatca|\basp\b|provider"),
    ("shield", r"verif|approv|complian|secure|active|accredit|protect"),
    ("clock", r"delay|follow-?up|minute|hour|deadline|schedule|remind|days? left|january|date"),
    ("branch", r"fork|parallel|\bif\b|block|branch|condition|route|workflow|rule|automat"),
    ("ticket", r"ticket|event|support|case|customer"),
    ("invoice", r"invoice|bill|receipt|credit note|refund|payment"),
    ("chart", r"report|dashboard|revenue|analytics|growth|sales"),
    ("gear", r"setting|setup|configur|enable|turn on|open"),
]


def pick_icon(text):
    t = (text or "").lower()
    return next((k for k, rx in KEYWORDS if re.search(rx, t)), "rocket")


def page_html(spec, w, h, dur):
    text = re.sub(r"\s+", " ", str(spec.get("text") or spec.get("card") or "")).strip()
    sub = str(spec.get("sub") or "").strip()
    pills = [p.strip() for p in re.split(r"\s*(?:>|›|→)\s*", sub) if p.strip()][:4] if sub else []
    beat = str(spec.get("beat") or "").upper()
    chip = (beat if beat.startswith("STEP") else {"FIX": "THE FIX", "HOOK": "NEW", "PROBLEM": "THE PROBLEM",
                                                  "RESULT": "THE RESULT"}.get(beat.split(" ")[0], "")).strip()
    acc = spec.get("accent") or "#2F6FEB"
    icon = spec.get("icon") or pick_icon(" ".join([text, sub, str(spec.get("say") or "")]))
    words = [_h.escape(x) for x in text.split()][:14]
    data = {"dur": dur, "paths": ICONS[icon], "n": len(words), "np": len(pills)}
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;overflow:hidden;font-family:'Poppins','Noto Sans',sans-serif;
  background:#FBFAF7}}
#grid{{position:absolute;inset:-60px;background:
  linear-gradient(rgba(30,36,51,.06) 2px,transparent 2px) 0 0/50px 50px,
  linear-gradient(90deg,rgba(30,36,51,.06) 2px,transparent 2px) 0 0/50px 50px}}
#blob{{position:absolute;width:760px;height:760px;border-radius:50%;left:120px;top:40px;
  background:radial-gradient(circle,{acc}33 0%,transparent 65%)}}
#chip{{position:absolute;left:50px;top:46px;background:{acc};color:#fff;font:800 40px Poppins,sans-serif;
  padding:12px 30px;border-radius:40px;letter-spacing:2px}}
svg{{position:absolute;left:{w // 2 - 220}px;top:110px}}
#pen{{position:absolute;width:26px;height:110px;border-radius:13px;background:linear-gradient({acc},#1E2433);
  transform-origin:50% 100%}}
#t{{position:absolute;left:60px;right:60px;top:590px;text-align:center;font:800 64px/1.12 Poppins,sans-serif;color:#1E2433}}
#t span{{display:inline-block;margin:0 9px}}
#t span.k{{color:{acc}}}
#p{{position:absolute;left:40px;right:40px;top:900px;text-align:center}}
.pl{{display:inline-block;margin:8px 6px;padding:12px 22px;border-radius:16px;background:#1E2433;color:#fff;
  font:700 30px Poppins,sans-serif}}
.ar{{display:inline-block;color:{acc};font:900 34px Poppins,sans-serif;margin:0 2px}}
#ok{{position:absolute;right:60px;top:60px}}
</style></head><body><div id="grid"></div><div id="blob"></div>
{f'<div id="chip">{_h.escape(chip)}</div>' if chip else ''}
<svg width="440" height="440" viewBox="0 0 300 300"><g id="ic" fill="none" stroke="#1E2433" stroke-width="11"
 stroke-linecap="round" stroke-linejoin="round"></g></svg><div id="pen"></div>
<div id="t">{''.join(f'<span class="{"k" if i >= len(words) - 2 else ""}">{x}</span>' for i, x in enumerate(words))}</div>
<div id="p">{''.join((f'<span class="ar">›</span>' if i else '') + f'<span class="pl">{_h.escape(p)}</span>'
                     for i, p in enumerate(pills))}</div>
<svg id="ok" width="120" height="120" viewBox="0 0 100 100" style="left:auto;top:40px;right:50px">
 <circle cx="50" cy="50" r="44" fill="#2E7D32" id="okc"/><path id="okp" d="M28 52 L44 67 L73 35" fill="none"
 stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>
<script>
const D={json.dumps(data)};
const ns='http://www.w3.org/2000/svg', g=document.getElementById('ic'), P=[];
for(const d of D.paths){{const p=document.createElementNS(ns,'path');p.setAttribute('d',d);g.appendChild(p);
  const L=p.getTotalLength();p.style.strokeDasharray=L;p.style.strokeDashoffset=L;P.push([p,L]);}}
const tot=P.reduce((a,x)=>a+x[1],0);
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), ease=x=>1-Math.pow(1-cl(x),3);
const back=x=>{{x=cl(x);const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}};
const W=document.querySelectorAll('#t span'), PL=document.querySelectorAll('#p > span');
const svgL={w // 2 - 220}, svgT=110, sc=440/300;
window.render=function(t){{
  const T=D.dur, draw=Math.min(1.6,T*0.35);
  document.getElementById('grid').style.transform=`translate(${{(t*12)%50}}px,${{(t*8)%50}}px)`;
  document.getElementById('blob').style.transform=`scale(${{1+0.06*Math.sin(t*2)}})`;
  const chip=document.getElementById('chip'); if(chip) chip.style.transform=`translateX(${{(1-ease(t/0.35))*-500}}px)`;
  let done=cl(t/draw)*tot, pen=null;
  for(const [p,L] of P){{const k=cl(done/L); p.style.strokeDashoffset=L*(1-k);
    if(k>0&&k<1&&!pen) pen=p.getPointAtLength(L*k); done-=L;}}
  const pe=document.getElementById('pen');
  if(pen){{pe.style.display='block';pe.style.left=(svgL+pen.x*sc-13)+'px';pe.style.top=(svgT+pen.y*sc-110)+'px';
    pe.style.transform='rotate(25deg)';}} else pe.style.display='none';
  // icon keeps breathing after it is drawn (never a frozen frame)
  g.style.transform=`translate(150px,150px) scale(${{1+0.035*Math.sin(t*3.2)}}) rotate(${{2*Math.sin(t*1.7)}}deg) translate(-150px,-150px)`;
  const t0=draw*0.55, per=Math.max(0.12,Math.min(0.28,(T*0.5)/Math.max(D.n,1)));
  W.forEach((s,i)=>{{const a=(t-t0-i*per)/0.22; s.style.opacity=cl(a*2); s.style.transform=`translateY(${{(1-ease(a))*40}}px) scale(${{a>0?back(a):0.6}})`;}});
  const p0=t0+D.n*per+0.15;
  PL.forEach((s,i)=>{{const a=(t-p0-i*0.18)/0.25; s.style.opacity=cl(a*2); s.style.transform=`scale(${{a>0?back(a):0.5}})`;}});
  const ok=(t-(T-1.1))/0.35, okp=document.getElementById('okp'), L=okp.getTotalLength();
  document.getElementById('ok').style.transform=`scale(${{ok>0?back(ok):0}})`; okp.style.strokeDasharray=L;
  okp.style.strokeDashoffset=L*(1-cl((t-(T-0.95))/0.4));
}};
window.render(0);
</script></body></html>"""


def render_panel(spec, frames, out: Path, w=1000, h=1100, fps=30):
    """Writes an MP4 of exactly `frames` frames (w x h) for one line."""
    from playwright.sync_api import sync_playwright
    out = Path(out)
    dur = frames / fps
    html = out.with_suffix(".html")
    html.write_text(page_html(spec, w, h, dur), encoding="utf-8")
    fonts = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps),
                           "-c:v", "mjpeg", "-i", "-", "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), "-an", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(html.resolve().as_uri(), wait_until="load")
        if (fonts / "Poppins-Bold.ttf").exists():
            pg.add_style_tag(content="@font-face{font-family:Poppins;src:url('%s');font-weight:700 900}"
                                     % (fonts / "Poppins-Bold.ttf").resolve().as_uri())
            pg.wait_for_timeout(150)
        for i in range(frames):
            pg.evaluate(f"render({i / fps})")
            ff.stdin.write(pg.screenshot(type="jpeg", quality=90))
        b.close()
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError(f"motion panel failed: {out}")
    return out
