"""Voice-over for a long video: one fixed voice for the whole video.

Engine tonight: Kokoro-82M via kokoro-onnx (code MIT, weights Apache-2.0 -> commercial OK, see docs/longform/TOOLS.md).
Later: Gaurav's own cloned voice (Chatterbox, MIT) - same interface: synth(text) -> (float32 mono, sr).

Every script line is synthesised on its own, leading/trailing silence trimmed, so we know exact line timings
(captions + animation cues are driven by them).
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

MODELS = Path(os.environ.get("LONGFORM_MODELS", Path.home() / ".cache" / "longform"))
URLS = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
SR = 24000

# how words are SAID (TTS) - the caption keeps the readable form (captions.py reverses the common ones)
SAY = [
    (r"\bZATCA\b", "Zatka"),
    (r"\bEmaraTax\b", "Emara Tax"),
]


def _models():
    MODELS.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        p = MODELS / name
        if not p.exists():
            print("download", name, flush=True)
            urllib.request.urlretrieve(url, p)
    return MODELS / "kokoro-v1.0.onnx", MODELS / "voices-v1.0.bin"


_K = None


def synth(text, voice="am_michael", speed=1.0):
    global _K
    if _K is None:
        from kokoro_onnx import Kokoro
        m, v = _models()
        _K = Kokoro(str(m), str(v))
    for a, b in SAY:
        text = re.sub(a, b, text)
    audio, sr = _K.create(text, voice=voice, speed=speed, lang="en-us")
    return np.asarray(audio, dtype=np.float32), sr


def trim(x, sr, thr=0.012, pad=0.04):
    a = np.abs(x)
    idx = np.where(a > thr)[0]
    if len(idx) == 0:
        return x
    s = max(0, idx[0] - int(pad * sr))
    e = min(len(x), idx[-1] + int(pad * 1.5 * sr))
    return x[s:e]


def build(script_path, out_dir):
    sc = json.loads(Path(script_path).read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v = sc.get("voice", {})
    meta = {}
    for scene in sc["scenes"]:
        lines = []
        for i, line in enumerate(scene["lines"]):
            f = out / f"{scene['id']}_{i}.wav"
            if not f.exists():
                x, sr = synth(line, v.get("voice", "am_michael"), v.get("speed", 1.0))
                x = trim(x, sr)
                sf.write(f, x, sr)
            info = sf.info(f)
            lines.append({"file": f.name, "dur": info.frames / info.samplerate})
        meta[scene["id"]] = lines
        print(scene["id"], [round(l["dur"], 2) for l in lines], flush=True)
    (out / "voice.json").write_text(json.dumps(meta, indent=1))
    return meta


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
