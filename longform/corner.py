"""Small round presenter "profile icon" in the corner (Gaurav, 14 Nov: tiny box, barely noticeable, he seems to be
talking - no photo with a mic stuck on it, no new Flow credits).

Source: an existing Flow clip of Gaurav talking (assets/base_clips/01.mp4). A face crop is played forward then backward
(ping-pong) so the loop has no jump, masked to a circle with a thin white ring, and laid over the finished video in
every scene except chapter cards and the outro.

  python -m longform.corner build out/video/corner.mov --size 200
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/base_clips/01.mp4"
CROP = "300:300:490:55"          # face square in the 1280x720 base clip
BASE = 150                       # diameter at 1080p; scaled with the render scale
MARGIN_R, MARGIN_B = 56, 74      # right / bottom margin at 1080p (above the progress bar, right of the captions)


def build(out, size):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    ring = out.with_suffix(".ring.png")
    mask = out.with_suffix(".mask.png")
    k = 4                                            # supersample for smooth edges
    m = Image.new("L", (size * k, size * k), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * k - 1, size * k - 1], fill=255)
    m.resize((size, size), Image.LANCZOS).save(mask)
    r = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(r)
    w = max(3, size // 40) * k
    d.ellipse([0, 0, size * k - 1, size * k - 1], outline=(255, 255, 255, 255), width=w)
    d.ellipse([w, w, size * k - 1 - w, size * k - 1 - w], outline=(15, 157, 138, 160), width=max(1, w // 3))
    r.resize((size, size), Image.LANCZOS).save(ring)
    fc = (f"[0:v]crop={CROP},trim=0.2:4.6,setpts=PTS-STARTPTS,scale={size}:{size}:flags=lanczos,eq=saturation=1.05,split[a][b];"
          f"[b]reverse[r];[a][r]concat=n=2:v=1:a=0,fps=30,format=rgba[v];[1:v]format=gray[m];[v][m]alphamerge[c];"
          f"[2:v]format=rgba[rg];[c][rg]overlay=0:0:format=auto,format=rgba[o]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SRC), "-i", str(mask), "-i", str(ring),
                    "-filter_complex", fc, "-map", "[o]", "-an", "-c:v", "qtrle", str(out)], check=True)
    return out


def ranges(scenes):
    """[(start, end)] where the corner shows: every scene except CHAPTER and OUTRO, neighbours merged."""
    out = []
    for s in scenes:
        if s["type"] in ("CHAPTER", "OUTRO"):
            continue
        a, b = s["start"], s["start"] + s["dur"]
        if out and abs(out[-1][1] - a) < 0.05:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def geometry(W, H, scale):
    size = int(round(BASE * scale / 2) * 2)
    x = W - size - int(MARGIN_R * scale)
    y = H - size - int(MARGIN_B * scale)
    return size, x, y


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2], int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 200)
