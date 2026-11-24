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


def face_crops(base, scenes):
    """square crop (x, y, side) around the presenter's face for every card scene (median of 5 frames)"""
    import cv2, statistics
    casc = cv2.CascadeClassifier("/tmp/cvx/cv2/data/haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(str(base)); out = []
    for sc in scenes:
        cs = []
        for k in range(5):
            t = sc["t0"] + (sc["t1"] - sc["t0"]) * (k + 0.5) / 5
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read()
            if not ok: continue
            g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
            f = casc.detectMultiScale(g, 1.1, 6, minSize=(120, 120))
            if len(f): x, y, w, h = max(f, key=lambda r: r[2] * r[3]); cs.append((x + w / 2, y + h / 2, w))
        if cs:
            fx = statistics.median(c[0] for c in cs); fy = statistics.median(c[1] for c in cs); fw = statistics.median(c[2] for c in cs)
            side = int(min(1080, max(360, fw * 1.7))) // 2 * 2
            x0 = int(min(max(0, fx - side / 2), 1080 - side)); y0 = int(min(max(0, fy - side * 0.45), 1920 - side))
        else:
            side, x0, y0 = 540, 270, 260
        out.append((x0, y0, side))
    cap.release(); return out


def main():
    sid = sys.argv[1]; clips = sys.argv[2:5]; test = sys.argv[6:] if len(sys.argv) > 5 and sys.argv[5] == "--test" else None
    S = SPEC[sid]; work = HERE / f"work_{sid}"; work.mkdir(exist_ok=True)
    # 1) trim every clip to its speech (+ small tails), normalise to 1080x1920@30
    segs, off, words = [], 0.0, []
    for i, c in enumerate(clips):
        T = dur(c); v = speech(c, T)
        a = max(0.0, v[0][0] - 0.10); b = min(T, v[-1][1] + 0.30)
        out = work / f"seg{i}.mp4"
        sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", c,
            "-vf", "crop=trunc(iw*0.94/2)*2:trunc(ih*0.94/2)*2:0:0,scale=1080:1920:flags=lanczos,fps=30,format=yuv420p", "-af", "aresample=48000,apad", "-t", f"{b - a:.3f}",
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
        norm = lambda x: re.sub(r"[^\w']", "", x).lower()
        for w in words:
            if w["clip"] == clip and norm(w["w"]) == norm(sub): return w["t0"]
        for w in words:
            if w["clip"] == clip and sub.lower() in w["w"].lower(): return w["t0"]
        raise KeyError((clip, sub))
    scenes = []
    for sc in S["scenes"]:
        sc = dict(sc)
        sc["t0"] = round(at(sc["clip"], sc["from"]) - 0.05, 3)
        sc["t1"] = round(at(sc.get("to_clip", sc["clip"]), sc["to"]) - 0.05 if sc.get("to") else segs[sc["clip"]][2], 3)
        scenes.append(sc)
    hook = {"html": S["hook"], "t0": 0.0, "t1": min(3.4, segs[0][2] - 0.2, min(x["t0"] for x in scenes) - 0.05)}
    cta = {"html": S["cta"], "t0": round(at(S.get("cta_clip", 3), S["cta_from"]) - 0.05, 3), "t1": total}
    pip = S.get("pip", {"x": 540, "y": 1100, "r": 155})
    data = {"dur": total, "words": words, "scenes": scenes, "hook": hook, "cta": cta, "pip": pip,
            "pill": S["pill"], "ticker": S["ticker"], "src": S["src"], "accent": S.get("accent"), "accent2": S.get("accent2")}
    json.dump(data, open(work / "data.json", "w"), indent=0)
    # 3) base video
    lst = work / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p, _, _ in segs))
    sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(work / "base.mov")])
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.add_init_script(f"window.DATA={json.dumps(data)};")
        pg.goto(f"file://{HERE}/jhpage.html"); pg.wait_for_timeout(500)
        if test is not None:
            for t in map(float, test):
                pg.evaluate(f"render({t})"); pg.screenshot(path=str(work / f"ov_{t:05.2f}.png"), omit_background=True)
            b.close(); print(json.dumps({"total": total, "scenes": [(s['t0'], s['t1']) for s in scenes]})); return
        nfr = int(total * FPS)
        # PIP: live face in a circle while a card is on screen - crop centred on the detected face of the clip below
        crops = face_crops(work / "base.mov", scenes)
        cx, cy, R = pip["x"], pip["y"], pip["r"]
        n = len(scenes)
        fc = f"[0:v]split={n + 1}[b]" + "".join(f"[p{j}]" for j in range(n)) + ";"
        for j, (sc, (x0, y0, side)) in enumerate(zip(scenes, crops)):
            fc += (f"[p{j}]crop={side}:{side}:{x0}:{y0},scale={2*R}:{2*R},format=rgba,"
                   f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lte(hypot(X-{R},Y-{R}),{R}),255,0)'[pc{j}];")
        fc += "[1:v]format=rgba[ov];[b][ov]overlay=0:0:eof_action=pass[x0];"
        for j, sc in enumerate(scenes):
            fc += (f"[x{j}][pc{j}]overlay={cx-R}:{cy-R}:enable='between(t,{sc['t0'] + 0.12:.3f},{sc['t1']:.3f})'"
                   + (f"[x{j + 1}];" if j < n - 1 else ",format=yuv420p[v]"))
        if n == 0: fc = "[1:v]format=rgba[ov];[0:v][ov]overlay=0:0,format=yuv420p[v]"
        print("crops", crops, flush=True)
        ov = work / "ov.mov"
        if not ov.exists():
            enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png",
                                    "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", str(ov) + ".tmp.mov"], stdin=subprocess.PIPE)
            for i in range(nfr):
                pg.evaluate(f"render({i / FPS})")
                enc.stdin.write(pg.screenshot(type="png", omit_background=True))
                if i % 150 == 0: print("frame", i, nfr, flush=True)
            enc.stdin.close(); enc.wait(); os.replace(str(ov) + ".tmp.mov", ov)
        b.close()
        sh(["ffmpeg", "-y", "-v", "error", "-i", str(work / "base.mov"), "-i", str(ov), "-filter_complex", fc,
            "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            str(work / "video.mp4")])

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
        "[0:a]aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2,aresample=48000,asplit[v][vk];[1:a]volume=0.5[s];"
        "[s][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[sd];"
        "[v][sd]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
        "-map", "[a]", "-ar", "48000", str(work / "audio.wav")])
    final = HERE / f"{sid}.mp4"
    sh(["ffmpeg", "-y", "-v", "error", "-i", str(work / "video.mp4"), "-i", str(work / "audio.wav"), "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)])
    print("done", final, round(total, 2))


if __name__ == "__main__":
    main()
