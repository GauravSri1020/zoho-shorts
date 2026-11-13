"""Long-video renderer: script JSON + voice lines -> timeline -> HTML scenes (Playwright) -> ffmpeg -> MP4.

  python -m longform.render docs/longform/scripts/uae-einvoicing.json --voice out/voice --out out/uae
      [--scale 1.3334 (=2560x1440) | 2 (=3840x2160)] [--only s04,s10] [--fps 30]

Steps: plan (timings, captions, voice level) -> per-scene MP4 segments (cached) -> audio mix
(voice + music bed + sfx, loudness-normalised) -> concat + mux -> QA (qa.py).
"""
import argparse
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
LEAD, GAP, TAIL = 0.35, 0.30, 0.45

# ---------- captions: readable form of what the voice says ----------
CAP = [
    (r"\bA S P\b", "ASP"), (r"\bT R N\b", "TRN"), (r"\bT I N\b", "TIN"), (r"\bF T A\b", "FTA"), (r"\bU U I D\b", "UUID"),
    (r"\bL L C\b", "LLC"), (r"\bI D\b", "ID"), (r"\bB to B\b", "B2B"), (r"\bB to C\b", "B2C"), (r"\bG S X\b", "GSX"),
    (r"Emara Tax", "EmaraTax"), (r"zero two three five", "0235"), (r"fifty million dirhams", "AED 50 million"),
    (r"five thousand dirhams", "AED 5,000"), (r"fifty thousand dirhams", "AED 50,000"), (r"one hundred dirhams", "AED 100"),
    (r"fourteen business days", "14 business days"), (r"ten digit", "10-digit"), (r"fifteen digit", "15-digit"),
    (r"first ten digits", "first 10 digits"), (r"five corner", "5-corner"), (r"twelve months", "12 months"),
    (r"Verify and Complete Setup", "Verify & Complete Setup"), (r"Taxes and Compliance", "Taxes & Compliance"),
]
DAYS = {"first": 1, "thirtieth": 30, "thirty first": 31}


def cap_text(s):
    for a, b in CAP:
        s = re.sub(a, b, s)
    s = re.sub(r"the (first|thirtieth|thirty first) of (\w+) (\d{4})", lambda m: f"{DAYS[m.group(1)]} {m.group(2)} {m.group(3)}", s)
    return s


def chunks(text, maxc=46):
    words = text.split()
    out, cur = [], []
    for w in words:
        cand = " ".join(cur + [w])
        if cur and (len(cand) > maxc or (re.search(r"[.?!]$", cur[-1]) and len(" ".join(cur)) > 14)):
            out.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
        if re.search(r"[,;:]$", w) and len(" ".join(cur)) > 26:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


# ---------- wav helpers (no soundfile needed) ----------
def read_wav(p):
    with wave.open(str(p)) as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        x = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768
        if ch > 1:
            x = x.reshape(-1, ch).mean(1)
    if sr != SR:
        idx = np.arange(int(len(x) * SR / sr)) * sr / SR
        x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    return x


def write_wav(p, x, ch=1):
    x = np.clip(x, -1, 1)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# ---------- plan ----------
def plan(script, voice_dir, fps):
    sc = json.loads(Path(script).read_text())
    vmeta = json.loads((Path(voice_dir) / "voice.json").read_text())
    idx = yaml.safe_load((ROOT / "assets/screens/index.yaml").read_text())["screens"]
    scenes, t = [], 0.0
    for s in sc["scenes"]:
        lines = vmeta[s["id"]]
        lead = 0.6 if s["type"] == "CHAPTER" else (0.25 if not scenes else LEAD)
        cues, cur = [], lead
        for i, l in enumerate(lines):
            cues.append({"s": round(cur, 3), "e": round(cur + l["dur"], 3), "text": s["lines"][i], "file": l["file"]})
            cur += l["dur"] + GAP
        dur = cur - GAP + (0.55 if s["type"] == "CHAPTER" else TAIL)
        if s["type"] == "OUTRO":
            dur += 1.5
        nfr = int(round(dur * fps))
        dur = nfr / fps
        caps = []
        for c in cues:
            txt = cap_text(c["text"])
            parts = chunks(txt)
            total = sum(len(p) for p in parts)
            ct = c["s"]
            for p in parts:
                d = (c["e"] - c["s"]) * len(p) / total
                caps.append({"s": round(ct, 3), "e": round(ct + d, 3), "text": p})
                ct += d
        screens = {}
        for a in s.get("visual", {}).get("actions", []):
            if a.get("screen"):
                screens[a["screen"]] = idx[a["screen"]]
        scenes.append({**s, "start": round(t, 4), "dur": dur, "frames": nfr, "cues": cues, "captions": caps, "screens": screens})
        t += dur
    total = t
    chap_starts = [x["start"] for x in scenes if x["type"] == "CHAPTER"]
    for x in scenes:
        x.update(total=total, chapters=sc["chapters"], chapterStarts=chap_starts)
    return sc, scenes, total


# ---------- audio ----------
def build_voice(scenes, voice_dir, total, fps):
    n = int((total + 1) * SR)
    v = np.zeros(n, np.float32)
    for s in scenes:
        for c in s["cues"]:
            x = read_wav(Path(voice_dir) / c["file"])
            a = int((s["start"] + c["s"]) * SR)
            v[a:a + len(x)] += x[: n - a]
    # per-scene level curve for the presenter (30 fps)
    hop = SR // 30
    rms = np.sqrt(np.convolve(v ** 2, np.ones(hop) / hop, mode="same")[::hop])
    ref = np.percentile(rms[rms > 1e-4], 95) if (rms > 1e-4).any() else 1
    lv = np.clip(rms / ref, 0, 1)
    for s in scenes:
        a = int(s["start"] * 30)
        s["level"] = [round(float(x), 3) for x in lv[a:a + int(s["dur"] * 30) + 2]]
    return v


def sfx(total, scenes):
    n = int((total + 1) * SR)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(7)

    def put(t, x, g):
        a = int(t * SR)
        if 0 <= a < n:
            out[a:a + len(x)] += (x * g)[: n - a]

    L = int(.55 * SR)
    tt = np.arange(L) / SR
    noise = rng.standard_normal(L).astype(np.float32)
    # whoosh: noise through a moving one-pole low-pass, swelling envelope
    cut = np.linspace(0.02, 0.35, L) ** 1.5
    y = np.zeros(L, np.float32)
    acc = 0.0
    for i in range(L):
        acc += cut[i] * (noise[i] - acc)
        y[i] = acc
    whoosh = y * np.sin(np.pi * np.clip(tt / .55, 0, 1)) ** 2
    whoosh /= np.abs(whoosh).max() + 1e-9
    click = (np.sin(2 * np.pi * 2400 * tt[:int(.03 * SR)]) * np.exp(-tt[:int(.03 * SR)] * 180)).astype(np.float32)
    thud = (np.sin(2 * np.pi * (90 * np.exp(-tt * 6) + 50) * tt) * np.exp(-tt * 9)).astype(np.float32)
    for s in scenes[1:]:
        put(s["start"] - .25, whoosh, .10 if s["type"] != "CHAPTER" else .16)
    for s in scenes:
        cue = lambda i, f=0: s["cues"][min(i, len(s["cues"]) - 1)]["s"] + f * (s["cues"][min(i, len(s["cues"]) - 1)]["e"] - s["cues"][min(i, len(s["cues"]) - 1)]["s"])
        for a in s.get("visual", {}).get("actions", []):
            if a.get("target") or a.get("box"):
                put(s["start"] + cue(a["cue"], a.get("at", 0)) + 1.15, click, .35)
        k = s.get("visual", {}).get("kind")
        if k == "penalty":
            put(s["start"] + cue(1, .3) + .33, thud, .5)
        if k == "record":
            put(s["start"] + s["cues"][3]["s"] + .1 + .33, thud, .4)
        if k == "outro":
            put(s["start"] + cue(0, .35), click, .4)
    return out


def music_bed(total, work):
    sys.path.insert(0, str(ROOT))
    try:
        from autopilot.music import generate          # read-only reuse of the Shorts' royalty-free generator
        p = generate(total + 1, Path(work) / "music.wav", seed=11)
        return read_wav(p)
    except Exception as e:                            # pragma: no cover
        print("music fallback:", e)
        return np.zeros(int((total + 1) * SR), np.float32)


def mix(scenes, voice_dir, total, work):
    v = build_voice(scenes, voice_dir, total, 30)
    m = music_bed(total, work)[: len(v)]
    m = np.pad(m, (0, len(v) - len(m)))
    # duck music under the voice (smooth envelope)
    env = np.abs(v)
    k = int(.25 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1 - 0.55 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
    bed = m * 0.085 * duck
    fx = sfx(total, scenes)
    write_wav(Path(work) / "voice.wav", v)
    write_wav(Path(work) / "mix_raw.wav", v + bed + fx)
    out = Path(work) / "mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(Path(work) / "mix_raw.wav"), "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", str(out)], check=True)
    return out


# ---------- video ----------
def render_scenes(scenes, work, scale, fps, only=None):
    from playwright.sync_api import sync_playwright
    seg = Path(work) / "seg"
    seg.mkdir(parents=True, exist_ok=True)
    W, H = int(round(1920 * scale / 2) * 2), int(round(1080 * scale / 2) * 2)
    stage = (ROOT / "longform/scenes/stage.html").as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale)
        page.goto(stage)
        page.evaluate("document.fonts.ready.then(()=>true)")
        for s in scenes:
            out = seg / f"{s['id']}.mp4"
            if only and s["id"] not in only and out.exists():
                continue
            if not only and out.exists():
                continue
            data = {k: v for k, v in s.items()}
            data["root"] = ROOT.as_uri()
            page.evaluate("d => window.setup(d)", data)
            page.wait_for_timeout(250)
            page.evaluate("() => Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => i.onload = i.onerror = r)))")
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                                   "-vf", f"scale={W}:{H}:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                                   "-r", str(fps), "-g", str(fps * 2), str(out) + ".tmp.mp4"], stdin=subprocess.PIPE)
            for i in range(s["frames"]):
                page.evaluate("t => window.render(t)", i / fps)
                ff.stdin.write(page.screenshot(type="jpeg", quality=93))
            ff.stdin.close()
            ff.wait()
            Path(str(out) + ".tmp.mp4").rename(out)
            print(f"[render] {s['id']} {s['type']} {s['dur']:.1f}s", flush=True)
        b.close()
    return seg


def concat(scenes, seg, audio, out):
    lst = Path(seg) / "list.txt"
    lst.write_text("".join(f"file '{s['id']}.mp4'\n" for s in scenes))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(audio),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--voice", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=float, default=1.3334)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--only", default="")
    ap.add_argument("--plan-only", action="store_true")
    a = ap.parse_args()
    work = Path(a.out)
    work.mkdir(parents=True, exist_ok=True)
    sc, scenes, total = plan(a.script, a.voice, a.fps)
    audio = mix(scenes, a.voice, total, work)
    (work / "plan.json").write_text(json.dumps(scenes, indent=1))
    print(f"[plan] {len(scenes)} scenes, {total / 60:.2f} min")
    if a.plan_only:
        return
    only = set(x for x in a.only.split(",") if x)
    seg = render_scenes(scenes, work, a.scale, a.fps, only)
    final = work / f"{sc['id']}.mp4"
    concat(scenes, seg, audio, final)
    print("[done]", final)


if __name__ == "__main__":
    main()
