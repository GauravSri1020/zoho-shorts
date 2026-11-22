"""PREMIUM middle part of a Zoho Short (23 Nov 2026, Gaurav: "beech mein gandi stuck screen aa rahi hai - jab mera
face hate to ya cartoon / whiteboard chale, ya screen-share jaisa screenshots pe kaam ho; premium lagna chahiye").

Every frame moves - nothing is ever a still photo:
  * REAL mode  - a real Zoho screenshot (assets/screens, spec "real") in a device frame on a dark glowing stage:
                 slides in, camera slowly pushes toward the click target, a cursor glides there, click ripple,
                 glowing highlight ring, step badge + title written on, menu path as animated chips.
  * BOARD mode - no real screenshot for this step (we never draw fake app pages any more): a whiteboard on the
                 dark stage - the step title is written on with a marker reveal, the menu path / keywords appear
                 as chips joined by drawn arrows, a big icon is drawn stroke by stroke, a check mark ticks at the end.
The presenter photo card is gone for good. Rendered frame by frame in headless Chromium (deterministic render(t)).

segments(items, outdir) -> list of mp4 paths; each item: {"frames", "mode", "step", "steps", "title", "tip",
"say", "accent", "img", "box", "header"}.
"""
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H, FPS = 1080, 1920, 30

ICONS = {  # simple line icons, drawn stroke by stroke (viewBox 0 0 120 120)
    "gear": "M60 38a22 22 0 1 0 0.1 0M60 14v12M60 94v12M14 60h12M94 60h12M27 27l9 9M84 84l9 9M27 93l9-9M84 36l9-9",
    "doc": "M34 14h38l20 20v72H34zM72 14v20h20M46 56h30M46 70h30M46 84h20",
    "check": "M24 62l24 24 50-52",
    "link": "M50 70l20-20M44 58l-12 12a14 14 0 0 0 20 20l12-12M76 62l12-12a14 14 0 0 0-20-20L56 42",
    "shield": "M60 12l38 14v30c0 26-17 44-38 52C39 100 22 82 22 56V26z M44 60l12 12 22-24",
    "flow": "M20 30h30v24H20zM70 66h30v24H70zM50 42h10v36h10",
    "chart": "M20 100V20M20 100h84M34 84l20-24 16 12 26-36",
    "mail": "M18 32h84v58H18zM18 32l42 32 42-32",
    "bolt": "M66 10L28 66h28l-6 44 40-58H62z",
}
_KEYS = [("check", r"verify|complete|active|done|ready|status"), ("shield", r"tax|complian|fta|zatca|vat|secure|legal"),
         ("mail", r"email|mail|notify|remind"), ("flow", r"rule|workflow|automation|block|event|fork|delay|flow"),
         ("link", r"connect|integrat|asp|emaratax|api|sync|link"), ("chart", r"report|analytics|dashboard|revenue"),
         ("doc", r"invoice|bill|document|pdf|note|quote"), ("gear", r"setting|setup|configure|studio|enable")]


def icon_for(text):
    t = (text or "").lower()
    for name, rx in _KEYS:
        if re.search(rx, t):
            return name
    return "bolt"


def chips_for(tip, title):
    """'Settings > Taxes & Compliance > E-Invoicing' -> ['Settings', 'Taxes & Compliance', 'E-Invoicing']"""
    src = tip or ""
    parts = [p.strip(" .") for p in re.split(r"\s*(?:>|›|→|:|\+)\s*", src) if p.strip(" .")]
    if len(parts) < 2:
        parts = [p.strip() for p in re.split(r"\s*(?:,|/| and )\s*", src) if p.strip()]
    parts = [p[:26] for p in parts if p.lower() != (title or "").lower()][:4]
    return parts


PAGE = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Anton;src:url(__FONTS__/Anton-Regular.ttf)}
@font-face{font-family:Pop;src:url(__FONTS__/Poppins-Bold.ttf);font-weight:700}
@font-face{font-family:Pop;src:url(__FONTS__/Poppins-Medium.ttf);font-weight:500}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#070a10}
#st{position:absolute;inset:0;overflow:hidden;font-family:Pop,sans-serif;color:#fff}
#bg{position:absolute;inset:-120px;background:linear-gradient(rgba(255,255,255,.05) 2px,transparent 2px) 0 0/80px 80px,
 linear-gradient(90deg,rgba(255,255,255,.05) 2px,transparent 2px) 0 0/80px 80px}
#g1,#g2{position:absolute;border-radius:50%}
#vg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 42%,transparent 40%,rgba(0,0,0,.8) 100%)}
#hdr{position:absolute;left:0;right:0;top:120px;text-align:center;font:700 40px Pop;letter-spacing:3px;color:rgba(255,255,255,.75)}
#badge{position:absolute;left:60px;top:205px;padding:10px 26px;border-radius:30px;font:700 34px Pop;letter-spacing:2px;color:#07090c}
#dots{position:absolute;right:60px;top:222px}
#dots i{display:inline-block;width:18px;height:18px;border-radius:9px;margin-left:12px;background:rgba(255,255,255,.25)}
#title{position:absolute;left:60px;right:60px;top:290px;font:400 92px/1.02 Anton;text-transform:uppercase}
#dev{position:absolute;left:60px;width:960px;top:560px;height:760px;border-radius:30px;overflow:hidden;background:#fff;
 box-shadow:0 40px 120px rgba(0,0,0,.7),0 0 0 3px rgba(255,255,255,.15)}
#bar{position:absolute;left:0;right:0;top:0;height:46px;background:#eef0f4;border-bottom:1px solid #d6d9e0}
#bar i{position:absolute;top:15px;width:16px;height:16px;border-radius:8px}
#cam{position:absolute;left:0;top:46px;right:0;bottom:0;overflow:hidden}
#img{position:absolute;left:0;top:0;transform-origin:0 0}
#ring{position:absolute;border:7px solid;border-radius:16px}
#cur{position:absolute;width:56px;height:56px}
#rip{position:absolute;border-radius:50%;border:6px solid}
#board{position:absolute;left:60px;width:960px;top:560px;height:780px;border-radius:30px;background:#fbfaf6;
 box-shadow:0 40px 120px rgba(0,0,0,.7);overflow:hidden}
#board:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent 0 58px,rgba(30,60,120,.05) 58px 60px)}
#ico{position:absolute;left:370px;top:50px}
#col{position:absolute;left:40px;right:40px;top:300px;text-align:center}#chips{min-height:100px}
.chip{display:inline-block;margin:12px 6px;padding:16px 26px;border-radius:18px;font:700 36px Pop;color:#13203a;
 background:#fff;border:4px solid #13203a;box-shadow:6px 6px 0 #13203a}
.arr{display:inline-block;font:700 44px Pop;color:#13203a;margin:0 2px;vertical-align:middle}
#say{margin:26px 30px 0;font:500 36px/1.35 Pop;color:#3a4357}
#chipsR{position:absolute;left:60px;right:60px;top:1350px;text-align:center}
#chipsR .chip{background:rgba(255,255,255,.08);color:#fff;border-color:rgba(255,255,255,.35);box-shadow:none;font-size:30px;padding:12px 20px}
#chipsR .arr{color:rgba(255,255,255,.6);font-size:34px}
#fl{position:absolute;inset:0;background:#fff;opacity:0}
</style></head><body><div id="st">
<div id="bg"></div><div id="g1"></div><div id="g2"></div>
__BODY__
<div id="vg"></div>
<div id="hdr"></div><div id="badge"></div><div id="dots"></div><div id="title"></div>
<div id="fl"></div></div>
<script>
const D=__DATA__;const $=i=>document.getElementById(i);
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=x=>1-Math.pow(1-cl(x),3);
const back=x=>{x=cl(x);const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
$('hdr').textContent=D.header||'';$('badge').textContent=D.step?('STEP '+D.step):'HOW IT WORKS';$('badge').style.background=D.accent;
for(let i=1;i<=(D.steps||0);i++){const e=document.createElement('i');if(i==D.step)e.style.background=D.accent;if(i<D.step)e.style.background='rgba(255,255,255,.6)';$('dots').appendChild(e);}
$('g1').style.cssText+=`left:-260px;top:300px;width:900px;height:900px;background:radial-gradient(circle,${D.accent}55,transparent 65%)`;
$('g2').style.cssText+=`right:-300px;top:900px;width:1000px;height:1000px;background:radial-gradient(circle,#2f6feb44,transparent 65%)`;
const TW=D.title.split(' ');
function chipsHTML(list,t,t0){let s='';list.forEach((c,i)=>{const p=back((t-t0-i*0.32)/0.35);if(p<=0.01)return;
 if(i)s+=`<span class="arr" style="opacity:${cl((t-t0-i*0.32)/.2)}">→</span>`;
 s+=`<span class="chip" style="transform:scale(${p});opacity:${cl(p)}">${c}</span>`;});return s;}
let iw=0,ih=0;
window.render=function(t){const T=D.dur;
 $('bg').style.transform=`translate(${(t*18)%80}px,${(t*30)%80}px)`;
 $('g1').style.transform=`translate(${Math.sin(t*.6)*60}px,${Math.cos(t*.5)*50}px)`;
 $('g2').style.transform=`translate(${Math.cos(t*.4)*70}px,${Math.sin(t*.7)*40}px)`;
 $('fl').style.opacity=Math.max(0,.35-t*2.2);
 $('badge').style.transform=`translateX(${(1-ease(t/.35))*-400}px)`;
 // title: words drop in one by one
 let n=0;$('title').innerHTML=TW.map((w,i)=>{const p=ease((t-0.15-i*0.09)/0.3);return `<span style="display:inline-block;opacity:${p};transform:translateY(${(1-p)*40}px)">${w}</span>`}).join(' ');
 if(D.mode==='real'){const dev=$('dev'),img=$('img');
  if(!iw){iw=img.naturalWidth||1;ih=img.naturalHeight||1;}
  const devH=760,camH=devH-46;dev.style.height=devH+'px';dev.style.top='560px';
  const p=ease((t-0.1)/0.5);dev.style.transform=`translateY(${(1-p)*500+Math.sin(t*1.8)*10}px) rotate(${Math.sin(t*1.1)*0.6}deg) scale(${0.9+0.1*p})`;dev.style.opacity=p;
  const [bx,by,bw,bh]=D.box;const sFit=Math.min(960/iw,camH/ih),sFill=Math.max(960/iw,camH/ih);
  // first the whole screen (where are we?), then the camera pushes in to the click target - like a screen share
  const k=ease((t-0.9)/(T*0.5));const drift=1+0.06*cl((t-0.9-T*0.5)/(T*0.5));const S=(sFit+(sFill*D.zoom-sFit)*k)*drift;
  const cx=(bx+bw/2),cy=(by+bh/2);
  let ox=480-cx*S, oy=camH/2-cy*S; ox=Math.min(0,Math.max(960-iw*S,ox));
  oy = ih*S<=camH ? (camH-ih*S)/2 : Math.min(0,Math.max(camH-ih*S,oy));
  img.style.width=iw+'px';img.style.transform=`translate(${ox}px,${oy}px) scale(${S})`;
  const tx=ox+cx*S,ty=oy+cy*S;const arrive=Math.min(T*0.6,2.2);const q=ease((t-0.6)/arrive);
  const sx=900,sy=camH-60;const cxp=sx+(tx-sx)*q,cyp=sy+(ty-sy)*q+Math.sin(q*Math.PI)*-60;
  const cur=$('cur');cur.style.left=cxp+'px';cur.style.top=cyp+'px';const tc=0.6+arrive;
  cur.style.transform=`scale(${t>tc&&t<tc+.18?0.85:1})`;
  const r=$('rip');const rp=(t-tc)/0.6;r.style.display=rp>0&&rp<1?'block':'none';const rr=20+rp*90;
  r.style.left=(tx-rr)+'px';r.style.top=(ty-rr)+'px';r.style.width=r.style.height=(2*rr)+'px';r.style.opacity=1-rp;r.style.borderColor=D.accent;
  const g=$('ring');const gp=cl((t-tc)/0.3);g.style.display=gp>0?'block':'none';const pad=10+4*Math.sin(t*6);
  g.style.left=(ox+bx*S-pad)+'px';g.style.top=(oy+by*S-pad)+'px';g.style.width=(bw*S+2*pad)+'px';g.style.height=(bh*S+2*pad)+'px';
  g.style.borderColor=D.accent;g.style.boxShadow=`0 0 ${20+10*Math.sin(t*6)}px ${D.accent}`;g.style.opacity=gp;
  $('chipsR').innerHTML=chipsHTML(D.chips,t,0.9);
 } else {const b=$('board');const p=ease((t-0.1)/0.45);b.style.transform=`translateY(${(1-p)*600}px) rotate(${(1-p)*4}deg)`;
  const pth=document.querySelectorAll('#ico path');pth.forEach(e=>{const L=e.getTotalLength();e.style.strokeDasharray=L;e.style.strokeDashoffset=L*(1-ease((t-0.5)/1.4));});
  $('ico').style.transform=`translateY(${Math.sin(t*2)*8}px)`;
  $('chips').innerHTML=chipsHTML(D.chips,t,1.0);
  const sp=cl((t-1.2)/0.5);$('say').style.opacity=sp;$('say').style.transform=`translateY(${(1-sp)*20}px)`;
  const ck=$('ck');const L=ck.getTotalLength();ck.style.strokeDasharray=L;ck.style.strokeDashoffset=L*(1-ease((t-(T-1.1))/0.5));
 }
};
window.render(0);
</script></body></html>"""

BODY_REAL = """<div id="dev"><div id="bar"><i style="left:22px;background:#ff5f57"></i><i style="left:48px;background:#febc2e"></i>
<i style="left:74px;background:#28c840"></i></div><div id="cam"><img id="img" src="__IMG__"><div id="ring"></div><div id="rip"></div>
<svg id="cur" viewBox="0 0 24 24"><path d="M3 2l7 19 2.6-7.4L20 11z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>
</div></div><div id="chipsR"></div>"""

BODY_BOARD = """<div id="board"><svg id="ico" width="220" height="220" viewBox="0 0 120 120">
<path d="__ICON__" fill="none" stroke="#13203a" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div id="col"><div id="chips"></div><div id="say">__SAY__</div></div>
<svg width="140" height="140" viewBox="0 0 120 120" style="position:absolute;right:36px;top:36px">
<circle cx="60" cy="60" r="50" fill="#1db954" opacity=".12"/><path id="ck" d="M30 62l20 20 40-44" fill="none" stroke="#1db954"
stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg></div>"""


def _page(item):
    mode = item.get("mode", "board")
    body = BODY_REAL if mode == "real" else BODY_BOARD
    say = html.escape(re.sub(r"\s+", " ", item.get("say", ""))[:150])
    body = (body.replace("__IMG__", Path(item["img"]).resolve().as_uri() if mode == "real" else "")
                .replace("__ICON__", ICONS[icon_for(" ".join([item.get("title", ""), item.get("tip", ""), item.get("say", "")]))])
                .replace("__SAY__", say))
    data = {"mode": mode, "title": html.escape(item.get("title", ""))[:60], "header": html.escape(item.get("header", ""))[:40],
            "step": item.get("step"), "steps": item.get("steps", 0), "accent": item.get("accent", "#E42527"),
            "chips": [html.escape(c) for c in item.get("chips", [])], "box": item.get("box") or [0, 0, 10, 10],
            "zoom": item.get("zoom", 1.3), "dur": item["frames"] / FPS}
    return PAGE.replace("__FONTS__", FONTS.resolve().as_uri()).replace("__BODY__", body).replace("__DATA__", json.dumps(data))


def segments(items, outdir: Path):
    from playwright.sync_api import sync_playwright
    outdir.mkdir(parents=True, exist_ok=True)
    outs = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": W, "height": H})
        for k, it in enumerate(items):
            f = outdir / f"prem{k:02d}.html"
            f.write_text(_page(it), encoding="utf-8")
            pg.goto(f.resolve().as_uri(), wait_until="load")
            pg.wait_for_timeout(250)
            out = outdir / f"prem{k:02d}.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                                   "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                                   "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)], stdin=subprocess.PIPE)
            for i in range(it["frames"]):
                pg.evaluate(f"render({i / FPS:.4f})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=90))
            ff.stdin.close()
            if ff.wait():
                raise RuntimeError(f"premium segment {k} failed to encode")
            outs.append(out)
            print(f"[premium] {it.get('mode')} step {it.get('step')}: {it['frames']} frames -> {out.name}")
        b.close()
    return outs
