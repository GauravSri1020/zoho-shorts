"""Background music bed.

1. If you put royalty-free tracks in assets/music/ (e.g. from the YouTube Audio Library), one is picked at random.
2. Otherwise a soft lo-fi bed is generated right here (chords + light beat), so there is never a copyright claim.
"""
import random
import wave
from pathlib import Path

import numpy as np

from .config import ASSETS_DIR

RATE = 44100


def _env(n, a=0.02, r=0.35):
    t = np.linspace(0, 1, n, endpoint=False)
    e = np.minimum(1, t / max(a, 1e-3)) * np.exp(-t / r)
    return e


def _note(f, dur, kind="pad"):
    n = int(dur * RATE)
    t = np.arange(n) / RATE
    if kind == "pad":
        x = 0.6 * np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t + 0.3) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
        x *= np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.5).clip(0, 1)
    elif kind == "pluck":
        x = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8)
    return x


def _kick(n):
    t = np.arange(n) / RATE
    f = 110 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 9)


def _hat(n, rng):
    t = np.arange(n) / RATE
    return rng.standard_normal(n) * np.exp(-t * 60) * 0.25


def _add(mix, s, x):
    e = min(len(mix), s + len(x))
    if e > s:
        mix[s:e] += x[:e - s]


def generate(seconds, out: Path, seed=None):
    rng = np.random.default_rng(seed)
    bpm = rng.choice([82, 86, 90, 94])
    beat = 60 / bpm
    bar = 4 * beat
    keys = [261.63, 293.66, 329.63, 349.23, 392.0]          # C D E F G roots
    root = rng.choice(keys) / 2
    # progressions in semitone offsets (I-V-vi-IV, vi-IV-I-V, I-vi-IV-V)
    prog = [[0, 7, 9, 5], [9, 5, 0, 7], [0, 9, 5, 7]][rng.integers(3)]
    total = int((seconds + 2) * RATE)
    mix = np.zeros(total)
    st = lambda s: root * 2 ** (s / 12)
    nbars = int(np.ceil((seconds + 2) / bar))
    for b in range(nbars):
        deg = prog[b % 4]
        minor = deg in (9, 2, 4)
        chord = [deg, deg + (3 if minor else 4), deg + 7, deg + 12]
        s0 = int(b * bar * RATE)
        for c in chord:
            x = _note(st(c) * 2, bar, "pad") * 0.10
            _add(mix, s0, x)
        for k in range(8):                                   # gentle arpeggio
            if rng.random() < 0.7:
                f = st(chord[k % 4] + 12) * 2
                x = _note(f, beat * 0.9, "pluck") * 0.06
                s = s0 + int(k * beat / 2 * RATE)
                _add(mix, s, x)
        for k in range(4):
            s = s0 + int(k * beat * RATE)
            if k in (0, 2):
                x = _kick(int(0.4 * RATE)) * 0.35
                _add(mix, s, x)
            for h in (0, 0.5):
                s2 = s + int(h * beat * RATE)
                x = _hat(int(0.08 * RATE), rng) * (0.5 if h else 0.3)
                _add(mix, s2, x)
    # soft low-pass (moving average) + fades
    k = 6
    mix = np.convolve(mix, np.ones(k) / k, mode="same")
    n = int(seconds * RATE)
    mix = mix[:n]
    fade = int(1.5 * RATE)
    mix[:fade] *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.8
    pcm = (mix * 32767).astype("<i2")
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    return out


def pick(seconds, workdir: Path, seed=None):
    tracks = [p for p in (ASSETS_DIR / "music").glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg")] \
        if (ASSETS_DIR / "music").exists() else []
    if tracks:
        t = random.Random(seed).choice(tracks)
        print(f"[music] {t.name}")
        return t
    print("[music] generated lo-fi bed")
    return generate(seconds, workdir / "music.wav", seed)
