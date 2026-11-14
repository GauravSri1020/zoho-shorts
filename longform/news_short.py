"""Vertical news Short from Flow avatar clips (Gaurav, 14 Nov: trending news Shorts "with my Flow").

  python -m longform.news_short spec.json clips_dir out.mp4

spec.json: {"banner": "...", "source": "...", "clips": [{"file": "A1.mp4", "text": "...", "lower": ["Name", "role"] | null}]}
Each clip: speech-trimmed (silence at start/end cut), zoomed slightly so the Veo watermark corner is cut away,
scaled to 1080x1920; burnt-in word-group captions (timed over the speech), a top news banner, an optional name
lower-third (the avatar never says real people's names - Flow refuses prominent names), a small source line,
a quiet royalty-free music bed (autopilot/music.py), loudness -14 LUFS.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets/fonts"
W, H = 1080, 1920


def speech_span(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=n=-35dB:d=0.25", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).groups()[2]) + 60 * float(re.search(r"Duration: (\d+):(\d+)", r).groups()[1])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    a, b = 0.0, dur
    if starts and starts[0] < 0.05 and ends:
        a = max(0.0, ends[0] - 0.08)
    if starts and starts[-1] > a + 1 and (len(ends) < len(starts) or ends[-1] >= dur - 0.05):
        b = min(dur, starts[-1] + 0.15)
    return round(a, 3), round(b, 3)


def ass_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def groups(text, n=3):
    w = text.split()
    out, cur = [], []
    for x in w:
        cur.append(x)
        if len(cur) >= n or re.search(r"[.,?!]$", x):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def build(spec_path, clips_dir, out):
    spec = json.loads(Path(spec_path).read_text())
    work = Path(out).with_suffix("")
    work.mkdir(parents=True, exist_ok=True)
    parts, t, events = [], 0.0, []
    for i, c in enumerate(spec["clips"]):
        src = Path(clips_dir) / c["file"]
        a, b = speech_span(src)
        d = b - a
        p = work / f"p{i}.mp4"
        # zoom 1.08 + slight upward crop: removes the Veo watermark in the lower-right corner
        vf = (f"trim={a}:{b},setpts=PTS-STARTPTS,scale={int(W * 1.08)}:{int(H * 1.08)}:flags=lanczos,"
              f"crop={W}:{H}:{int(W * .04)}:{int(H * .03)},fps=30,format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf,
                        "-af", f"atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "17", "-c:a", "aac", "-b:a", "192k", str(p)], check=True)
        gs = groups(c["text"])
        tot = sum(len(g) for g in gs)
        ct = t
        for g in gs:
            gd = d * len(g) / tot
            events.append(("Cap", ct, ct + gd, g.upper()))
            ct += gd
        if c.get("lower"):
            events.append(("Lower", t + .2, t + d - .1, c["lower"][0]))
            events.append(("Role", t + .2, t + d - .1, c["lower"][1]))
        parts.append(p)
        t += d
    total = t
    events.append(("Banner", 0, total, spec["banner"]))
    events.append(("Src", 0, total, spec["source"]))
    ass = work / "subs.ass"
    ass.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Poppins,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,2,2,60,60,560,1
Style: Banner,Poppins,54,&H00FFFFFF,&H00FFFFFF,&H002E2EE0,&H002E2EE0,1,0,0,0,100,100,1,0,3,18,0,8,60,60,120,1
Style: Lower,Poppins,58,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,3,16,0,1,70,60,860,1
Style: Role,Poppins,40,&H00FFFFFF,&H00FFFFFF,&H00202020,&H00202020,0,0,0,0,100,100,0,0,3,12,0,1,70,60,790,1
Style: Src,Poppins,30,&H00E6E6E6,&H00E6E6E6,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,2,1,2,60,60,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "".join(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},{st},,0,0,0,,{txt}\n" for st, a, b, txt in events))
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    joined = work / "joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    music = work / "music.wav"
    try:
        sys.path.insert(0, str(ROOT))
        from autopilot.music import generate
        generate(total + 1, music, seed=23)
    except Exception as e:                                           # pragma: no cover
        print("no music:", e)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", str(total + 1), str(music)], check=True)
    fc = (f"[0:v]ass={ass}:fontsdir={FONT_DIR}[v];[1:a]volume=0.07[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(joined), "-i", str(music), "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(f"[news_short] {out} {total:.1f}s")
    return total


if __name__ == "__main__":
    build(*sys.argv[1:4])
