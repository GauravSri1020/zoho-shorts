"""Find single-frame glitches (half-painted frames): frame i differs from both neighbours, neighbours agree.
python -m longform.glitch video.mp4 [plan.json]  -> prints times (+ scene ids)"""
import json
import subprocess
import sys

import numpy as np


def main(video, plan=None):
    w, h = 192, 108
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    prev2 = prev = None
    i = 0
    hits = []
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            break
        f = np.frombuffer(b, np.uint8).astype(np.int16)
        if prev2 is not None:
            bm = lambda d: d.reshape(h // 12, 12, w // 12, 12).mean(axis=(1, 3))
            A, Cc, N = bm(np.abs(prev - prev2)), bm(np.abs(f - prev)), bm(np.abs(f - prev2))
            k = np.unravel_index(np.argmax(np.minimum(A, Cc)), A.shape)
            a, c, n = A[k], Cc[k], N[k]
            if min(a, c) > 8 and n < 0.3 * min(a, c):
                hits.append(round((i - 1) / 30, 3))
        prev2, prev = prev, f
        i += 1
    sc = json.load(open(plan)) if plan else []
    ids = sorted({s["id"] for t in hits for s in sc if s["start"] <= t < s["start"] + s["dur"]})
    print(json.dumps({"frames": i, "glitches": hits, "scenes": ids}))


if __name__ == "__main__":
    main(*sys.argv[1:])
