"""AI voice for the avatar (this is synthetic media -> the video is uploaded with YouTube's AI label on).

Main engine: Gemini TTS (free tier, REST). Fallback: edge-tts, so the channel never misses a day.
"""
import asyncio
import base64
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

from .config import GEMINI_API_KEY, CH

_V = CH.get("avatar", {})
GEMINI_VOICE = os.getenv("TTS_VOICE") or _V.get("gemini_voice", "Puck")
BACKUP_VOICE = _V.get("backup_voice", "hi-IN-MadhurNeural")
STYLE = _V.get("voice_style", "confident, friendly Hinglish explainer, Indian accent, natural pace")
TEMPO = float(os.getenv("TTS_TEMPO") or _V.get("tempo", 1.05))
TTS_MODELS = [m.strip() for m in os.getenv(
    "GEMINI_TTS_MODELS", "gemini-3.8-flash-tts,gemini-2.5-flash-preview-tts,gemini-2.5-pro-preview-tts").split(",") if m.strip()]
RATE = 24000
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout.strip())


def _clean(text):
    return re.sub(r"\s+", " ", re.sub(r"[\[<][^\]>]{1,30}[\]>]", "", text or "")).strip()


def _spoken(lines):
    return " ".join(_clean(l.get("tts") or l.get("say")) for l in lines)


def _post(model, text):
    body = {"contents": [{"role": "user", "parts": [{"text": f"Say this as a {STYLE}:\n\n{text}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": GEMINI_VOICE}}}}}
    req = urllib.request.Request(API.format(model=model), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='ignore')[:300]}") from None
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    raw = b"".join(base64.b64decode(p["inlineData"]["data"]) for p in parts if p.get("inlineData"))
    if not raw:
        raise RuntimeError(f"no audio in response: {str(data)[:200]}")
    return raw


def _write_pcm(raw, path):
    if raw[:4] == b"RIFF":
        tmp = path.with_suffix(".in.wav")
        tmp.write_bytes(raw)
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-ar", str(RATE), "-ac", "1", str(path)])
        return
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(raw)


def _gemini(text, path):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY missing")
    last = None
    for model in TTS_MODELS:
        for attempt in range(2):
            try:
                _write_pcm(_post(model, text), path)
                if duration(path) < 8:
                    raise RuntimeError("audio too short")
                print(f"[voice] ok via {model}")
                return
            except Exception as e:
                last = e
                print(f"[voice] {model} try {attempt + 1}: {str(e)[:200]}")
                if "HTTP 400" in str(e) or "HTTP 404" in str(e):
                    break
                time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"Gemini TTS failed: {last}")


def _edge(text, path):
    import edge_tts

    async def go():
        mp3 = path.with_suffix(".mp3")
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, BACKUP_VOICE, rate="+8%").save(str(mp3))
                break
            except Exception as e:
                print(f"[voice] edge retry {attempt + 1}: {e}")
                await asyncio.sleep(5 * (attempt + 1))
        else:
            raise RuntimeError("edge-tts failed")
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", str(RATE), "-ac", "1", str(path)])
    asyncio.run(go())


def synthesize(lines, workdir: Path, max_seconds: float):
    """Returns (final 44.1 kHz wav, engine)."""
    workdir.mkdir(parents=True, exist_ok=True)
    text, raw = _spoken(lines), workdir / "raw.wav"
    engine = "gemini"
    try:
        _gemini(text, raw)
    except Exception as e:
        print(f"[voice] falling back to edge-tts: {str(e)[:200]}")
        engine = "edge"
        _edge(text, raw)
    d = duration(raw)
    tempo = TEMPO if 0.5 <= TEMPO <= 2.0 else 1.0
    if d / tempo > max_seconds - 0.5:
        tempo = min(d / (max_seconds - 0.5), 1.3)
    final = workdir / "voice.wav"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
          f"atempo={tempo:.4f},loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "44100", "-ac", "1", str(final)])
    print(f"[voice] engine={engine} raw={d:.1f}s tempo={tempo:.2f} final={duration(final):.1f}s")
    return final, engine
