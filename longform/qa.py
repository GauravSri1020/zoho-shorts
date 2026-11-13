"""Strict QA for a long video (blocks upload on any failure).

  python -m longform.qa out/uae/uae-einvoicing.mp4 --voice out/uae/voice.wav

Checks: duration 7-12 min, 16:9, no black frames (blackdetect), no dead air (> 1.2 s without voice inside the video,
measured on the voice-only track), loudness around -14 LUFS, audio + video same length.
"""
import argparse
import json
import re
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--voice", required=True)
    ap.add_argument("--max-gap", type=float, default=1.2)
    a = ap.parse_args()
    probs = []
    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", a.video]).stdout)
    v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
    au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
    dur = float(pr["format"]["duration"])
    info = {"duration_s": round(dur, 2), "size": f"{v['width']}x{v['height']}", "fps": v["r_frame_rate"]}
    if not 420 <= dur <= 720:
        probs.append(f"duration {dur:.0f}s not 7-12 min")
    if abs(v["width"] / v["height"] - 16 / 9) > 0.01:
        probs.append("not 16:9")
    if not au:
        probs.append("no audio")
    else:
        ad = float(au[0].get("duration", dur))
        if abs(ad - float(v.get("duration", dur))) > 0.5:
            probs.append(f"audio/video length differ ({ad:.2f} vs {v.get('duration')})")
    bd = run(["ffmpeg", "-hide_banner", "-i", a.video, "-vf", "blackdetect=d=0.04:pix_th=0.08", "-an", "-f", "null", "-"]).stderr
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)
    info["black_segments"] = blacks
    if blacks:
        probs.append(f"black frames at {blacks[:5]}")
    sd = run(["ffmpeg", "-hide_banner", "-i", a.voice, "-af", f"silencedetect=n=-45dB:d={a.max_gap}", "-f", "null", "-"]).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", sd)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", sd)]
    gaps = [(s, e) for s, e in zip(starts, ends + [dur]) if s > 0.5 and e < dur - 3.0]
    info["dead_air"] = gaps
    if gaps:
        probs.append(f"dead air > {a.max_gap}s at {[(round(s, 1), round(e, 1)) for s, e in gaps[:5]]}")
    ln = run(["ffmpeg", "-hide_banner", "-i", a.video, "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", ln)
    if m:
        info["lufs"] = float(m[-1])
        if not -16.5 <= float(m[-1]) <= -12.5:
            probs.append(f"loudness {m[-1]} LUFS")
    info["problems"] = probs
    print(json.dumps(info, indent=1))
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
