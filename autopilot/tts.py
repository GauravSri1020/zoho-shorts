"""Voice for the Zoho-screen parts (the presenter's face is only on screen for HOOK / PROBLEM / RESULT).

Order: Gemini TTS (same prebuilt voice the Flow avatar uses, e.g. "Achird")
    -> edge-tts (free Microsoft neural voice, no key)
    -> Piper (offline neural voice, runs on the GitHub runner itself - never blocked, never out of quota).
Once a provider is out of quota / blocked in this run it is skipped for the rest of the run (no long retries).
Output: mono 44.1 kHz wav.
"""
import os
import subprocess
import time
import wave
from pathlib import Path

from .config import CH, GEMINI_API_KEY

_F = CH.get("flow", {}) or {}
VOICE = str(_F.get("voice", "Achird"))
STYLE = str(_F.get("voice_style", "Say this like a friendly, energetic YouTube tech explainer, clear natural "
                                  "English with a neutral international accent, brisk pace"))
BACKUP_VOICE = str(_F.get("backup_voice", "en-GB-RyanNeural"))
PIPER_VOICE = str(_F.get("piper_voice", "en_US-ryan-high"))
PIPER_DIR = Path(os.getenv("PIPER_DIR", str(Path.home() / ".cache" / "piper")))
MODELS = [m for m in [os.getenv("TTS_MODEL", ""), *(_F.get("tts_models") or []),
                      "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"] if m]

_DEAD = set()  # providers that are out of quota / blocked for this run


def _pcm_to_wav(pcm: bytes, path: Path, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def _gemini(text, raw: Path):
    from google import genai
    from google.genai import types
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY missing")
    client = genai.Client(api_key=GEMINI_API_KEY)
    last = None
    quota_hits = 0
    for attempt in range(4):
        model = MODELS[attempt % len(MODELS)]
        try:
            r = client.models.generate_content(
                model=model, contents=f"{STYLE}: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)))))
            part = r.candidates[0].content.parts[0]
            data = part.inline_data.data
            mime = str(getattr(part.inline_data, "mime_type", "") or "")
            sr = 24000
            if "rate=" in mime:
                try:
                    sr = int(mime.split("rate=")[1].split(";")[0])
                except ValueError:
                    pass
            _pcm_to_wav(data, raw, sr)
            return
        except Exception as e:
            last = e
            msg = str(e)
            print(f"[tts] {model} attempt {attempt + 1} failed: {msg[:160]}")
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                quota_hits += 1
                if quota_hits >= len(MODELS):  # every model is out of quota -> stop wasting time this run
                    _DEAD.add("gemini")
                    break
                continue
            time.sleep(0 if "404" in msg else min(4 * (attempt + 1), 15))
    raise RuntimeError(f"Gemini TTS unavailable: {str(last)[:160]}")


def _edge(text, raw: Path):
    """Free Microsoft neural voice (no key)."""
    import asyncio
    import edge_tts
    mp3 = raw.with_suffix(".edge.mp3")
    try:
        asyncio.run(edge_tts.Communicate(text, BACKUP_VOICE, rate="+8%").save(str(mp3)))
        if not mp3.exists() or mp3.stat().st_size < 1000:
            raise RuntimeError("edge-tts returned no audio")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", "24000", str(raw)],
                       check=True)
    except Exception:
        _DEAD.add("edge")  # 403 / network block is not going to fix itself inside this run
        raise
    finally:
        mp3.unlink(missing_ok=True)


def _piper_model():
    PIPER_DIR.mkdir(parents=True, exist_ok=True)
    onnx = PIPER_DIR / f"{PIPER_VOICE}.onnx"
    if not onnx.exists() or not (PIPER_DIR / f"{PIPER_VOICE}.onnx.json").exists():
        from piper.download_voices import download_voice
        download_voice(PIPER_VOICE, PIPER_DIR)
    return onnx


def _piper(text, raw: Path):
    """Offline neural TTS on the runner CPU (piper-tts). Always available."""
    from piper import PiperVoice
    voice = PiperVoice.load(str(_piper_model()))
    syn = None
    try:
        from piper import SynthesisConfig
        syn = SynthesisConfig(length_scale=0.92)  # a little brisker, like the avatar
    except Exception:
        pass
    with wave.open(str(raw), "wb") as w:
        if syn is not None:
            voice.synthesize_wav(text, w, syn_config=syn)
        else:
            voice.synthesize_wav(text, w)


def speak(text, out_wav: Path, rate=44100):
    """text -> out_wav (mono, `rate` Hz), leading/trailing silence trimmed. Returns the length in seconds."""
    raw = out_wav.with_suffix(".raw.wav")
    errors = []
    for name, fn in (("gemini", _gemini), ("edge", _edge), ("piper", _piper)):
        if name in _DEAD:
            continue
        try:
            fn(text, raw)
            if name != "gemini":
                print(f"[tts] used backup voice: {name}")
            break
        except Exception as e:
            errors.append(f"{name}: {str(e)[:140]}")
            print(f"[tts] {name} failed -> next ({str(e)[:140]})")
    else:
        raise RuntimeError("all TTS providers failed: " + " | ".join(errors))
    # trim silence at both ends, resample
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ac", "1", "-ar", str(rate),
                    "-c:a", "pcm_s16le", str(out_wav)], check=True)
    raw.unlink(missing_ok=True)
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(out_wav)], capture_output=True, text=True, check=True).stdout.strip())
