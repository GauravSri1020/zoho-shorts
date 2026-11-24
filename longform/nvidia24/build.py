"""NVIDIA news Shorts (24 Nov 2026): 4 Flow face clips + kinetic news cards + live face PIP + word captions.
usage: python3 build.py A clip1.mp4 clip2.mp4 clip3.mp4 clip4.mp4 [--test t1 t2 ...]"""
import json, re, subprocess, sys, os
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
FPS = 30
SPEC = json.load(open(HERE / "spec.json"))


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def dur(p):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).stdout)


def speech(p, total):
    """voiced intervals [(a,b)] from silencedetect"""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "silencedetect=n=-34dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    sil, s0 = [], None
    for ln in out.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", ln)
        if m: s0 = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", ln)
        if m: sil.append((s0 or 0.0, float(m.group(1)))); s0 = None
    if s0 is not None: sil.append((s0, total))
    v, cur = [], 0.0
    for a, b in sil:
        if a > cur + 0.05: v.append((cur, a))
        cur = max(cur, b)
    if cur < total - 0.05: v.append((cur, total))
    return v or [(0, total)]


def main():
    sid = sys.argv[1]; clips = sys.argv[2:6]; test = sys.argv[7:] if len(sys.argv) > 6 and sys.argv[6] == "--test" else None
    S = SPEC[sid]; work = HERE / f"work_{sid}"; work.mkdir(exist_ok=True)
    # 1) trim every clip to its speech (+ small tails), normalise to 1080x1920@30
    segs, off, words = [], 0.0, []
    for i, c in enumerate(clips):
        T = dur(c); v = speech(c, T)
        a = max(0.0, v[0][0] - 0.10); b = min(T, v[-1][1] + 0.30)
        out = work / f"seg{i}.mp4"
        sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", c,
            "-vf", "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p", "-af", "aresample=48000",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "pcm_s16le", str(out).replace(".mp4", ".mov")])
        out = Path(str(out).replace(".mp4", ".mov")); d = dur(out)
        vv = [(max(0, x - a), min(d, y - a)) for x, y in v if y > a and x < b]
        # 2) word times: spread the known words over the voiced time, weighted by length
        toks = S["clips"][i].split()
        wts = [max(2, len(re.sub(r"[^\w$%.]", "", t))) + 1.0 for t in toks]
        vt = sum(y - x for x, y in vv); per = vt / sum(wts)
        k, pos = 0, 0.0
        for tok, w in zip(toks, wts):
            need = w * per; t0 = None
            while need > 1e-6 and k < len(vv):
                x, y = vv[k]; st = x + pos
                if t0 is None: t0 = st
                take = min(need, y - st); need -= take; pos += take
                if x + pos >= y - 1e-6: k += 1; pos = 0.0
            t1 = (vv[k][0] + pos) if k < len(vv) else vv[-1][1]
            words.append({"w": tok.strip(), "t0": round(off + (t0 or 0), 3), "t1": round(off + t1, 3), "clip": i,
                          "hl": bool(re.search(r"\d", tok)) or re.sub(r"[^\w]", "", tok).lower() in S.get("hl", [])})
        segs.append((out, off, off + d)); off += d
    total = off
    # caption groups: <=3 words, break after punctuation
    g, n = 0, 0
    for j, w in enumerate(words):
        w["g"] = g; n += 1
        if n == 3 or re.search(r"[.,?!]$", w["w"]) or (j + 1 < len(words) and words[j + 1]["clip"] != w["clip"]):
            g += 1; n = 0
    for j, w in enumerate(words):
        last = max(x["t1"] for x in words if x["g"] == w["g"])
        nxt = next((x["t0"] for x in words if x["g"] == w["g"] + 1), total)
        w["gend"] = round(min(last + 0.35, nxt - 0.01), 3)

    def at(clip, sub):
        for w in words:
            if w["clip"] == clip and sub.lower() in w["w"].lower(): return w["t0"]
        raise KeyError((clip, sub))
    scenes = []
    for sc in S["scenes"]:
        sc = dict(sc)
        sc["t0"] = round(at(sc["clip"], sc["from"]) - 0.05, 3)
        sc["t1"] = round(at(sc["clip"], sc["to"]) - 0.05 if sc.get("to") else segs[sc["clip"]][2], 3)
        scenes.append(sc)
    hook = {"html": S["hook"], "t0": 0.0, "t1": min(3.6, segs[0][2] - 0.2)}
    cta = {"html": S["cta"], "t0": round(at(3, S["cta_from"]) - 0.05, 3), "t1": total}
    pip = S.get("pip", {"x": 540, "y": 1100, "r": 155})
    data = {"dur": total, "words": words, "scenes": scenes, "hook": hook, "cta": cta, "pip": pip,
            "pill": S["pill"], "ticker": S["ticker"], "src": S["src"]}
    json.dump(data, open(work / "data.json", "w"), indent=0)
    # 3) base video
    lst = work / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p, _, _ in segs))
    sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(work / "base.mov")])
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.add_init_script(f"window.DATA={json.dumps(data)};")
        pg.goto(f"file://{HERE}/nvpage.html"); pg.wait_for_timeout(500)
        if test is not None:
            for t in map(float, test):
                pg.evaluate(f"render({t})"); pg.screenshot(path=str(work / f"ov_{t:05.2f}.png"), omit_background=True)
            b.close(); print(json.dumps({"total": total, "scenes": [(s['t0'], s['t1']) for s in scenes]})); return
        nfr = int(total * FPS)
        # PIP: live face in a circle while a card is on screen
        en = "+".join(f"between(t,{s['t0'] + 0.12:.3f},{s['t1']:.3f})" for s in scenes) or "0"
        cx, cy, R = pip["x"], pip["y"], pip["r"]; cr = S.get("crop", [270, 300, 540])
        fc = (f"[0:v]split[b][p];[p]crop={cr[2]}:{cr[2]}:{cr[0]}:{cr[1]},scale={2*R}:{2*R},format=rgba,"
              f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lte(hypot(X-{R},Y-{R}),{R}),255,0)'[pc];"
              f"[1:v]format=rgba[ov];[b][ov]overlay=0:0:eof_action=pass[x];"
              f"[x][pc]overlay={cx-R}:{cy-R}:enable='{en}',format=yuv420p[v]")
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-i", str(work / "base.mov"),
                               "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                               "-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast",
                               "-crf", "18", "-pix_fmt", "yuv420p", str(work / "video.mp4")], stdin=subprocess.PIPE)
        for i in range(nfr):
            pg.evaluate(f"render({i / FPS})")
            ff.stdin.write(pg.screenshot(type="png", omit_background=True))
            if i % 150 == 0: print("frame", i, nfr, flush=True)
        ff.stdin.close(); ff.wait(); b.close()
    # 4) audio: voice + SFX (whoosh on every card / CTA, pop on stamps) + soft pulse bed, then loudnorm
    sfx = work / "sfx.wav"
    hits = [s["t0"] for s in scenes] + [cta["t0"]]
    pops = [s["t0"] + s.get("stampAt", 0.9) for s in scenes if s.get("stamp")]
    parts, inputs = [], []
    whoosh = "anoisesrc=d=0.45:c=pink:a=0.9,highpass=f=300,lowpass=f=5000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2,volume=0.55"
    pop = "sine=f=180:d=0.18,afade=t=out:d=0.18,volume=0.9"
    fl = []
    for k, t in enumerate(hits):
        fl.append(f"{whoosh},adelay={int(max(0, t - 0.2) * 1000)}|{int(max(0, t - 0.2) * 1000)},aformat=channel_layouts=stereo[w{k}]")
    for k, t in enumerate(pops):
        fl.append(f"{pop},adelay={int(t * 1000)}|{int(t * 1000)},aformat=channel_layouts=stereo[p{k}]")
    bed = (f"aevalsrc='0.05*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.035*sin(2*PI*164.8*t)+0.03*sin(2*PI*220*t)"
           f"+0.22*sin(2*PI*52*t)*exp(-9*mod(t,0.5))':s=48000:d={total:.2f},aformat=channel_layouts=stereo,volume=0.55[bed]")
    labels = "".join(f"[w{k}]" for k in range(len(hits))) + "".join(f"[p{k}]" for k in range(len(pops))) + "[bed]"
    fl.append(bed)
    fl.append(f"{labels}amix=inputs={len(hits) + len(pops) + 1}:normalize=0,atrim=0:{total:.2f}[s]")
    sh(["ffmpeg", "-y", "-v", "error", "-filter_complex", ";".join(fl), "-map", "[s]", str(sfx)])
    sh(["ffmpeg", "-y", "-v", "error", "-i", str(work / "base.mov"), "-i", str(sfx), "-filter_complex",
        "[0:a]aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2,asplit[v][vk];[1:a]volume=0.5[s];"
        "[s][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[sd];"
        "[v][sd]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
        "-map", "[a]", "-ar", "48000", str(work / "audio.wav")])
    final = HERE / f"nvidia_{sid}.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-i", str(work / "video.mp4"), "-i", str(work / "audio.wav"), "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)])
    print("done", final, round(total, 2))


if __name__ == "__main__":
    main()
