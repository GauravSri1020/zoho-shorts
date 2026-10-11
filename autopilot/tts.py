"""Voice for the Zoho-screen parts (the presenter's face is only on screen for HOOK / PROBLEM / RESULT).

Gemini TTS with the SAME prebuilt voice the Flow avatar uses (Flow voices are Gemini voices, e.g. "Achird"),
so the screen parts sound like the presenter. Falls back to the next model, then fails loudly.
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
                                    "English with an Indian accent, brisk pace"))
MODELS = [m for m in [os.getenv("TTS_MODEL", ""), *(_F.get("tts_models") or []),
                      "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts"] if m]


def _pcm_to_wav(pcm: bytes, path: Path, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def speak(text, out_wav: Path, rate=44100):
    """text -> out_wav (mono, `rate` Hz), leading/trailing silence trimmed. Returns the length in seconds."""
    from google import genai
    from google.genai import types
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY missing (needed for the screen-part voice)")
    client = genai.Client(api_key=GEMINI_API_KEY)
    raw = out_wav.with_suffix(".raw.wav")
    last = None
    for attempt in range(6):
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
            break
        except Exception as e:
            last = e
            print(f"[tts] {model} attempt {attempt + 1} failed: {str(e)[:160]}")
            time.sleep(0 if "404" in str(e) else min(6 * (attempt + 1), 30))
    else:
        raise RuntimeError(f"TTS failed: {last}")
    # trim silence at both ends, resample
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ac", "1", "-ar", str(rate),
                    "-c:a", "pcm_s16le", str(out_wav)], check=True)
    raw.unlink(missing_ok=True)
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(out_wav)], capture_output=True, text=True, check=True).stdout.strip())
