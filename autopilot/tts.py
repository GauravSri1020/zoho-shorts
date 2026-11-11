"""Voice for the Zoho-screen parts (the presenter's face is only on screen for HOOK / PROBLEM / RESULT).

Order: Gemini TTS (same prebuilt voice the Flow avatar uses, e.g. "Achird")
    -> edge-tts (free Microsoft neural voice, no key)
    -> Piper (offline neural voice, runs on the GitHub runner itself - never blocked, never out of quota).
Once a provider is out of quota / blocked in this run it is skipped for the rest of the run.
Gemini: a per-MINUTE rate limit (429) is waited out (retryDelay) - same voice, nothing changes. Only when the DAILY
quota of every Gemini TTS model is used up does the backup voice take over.
speak_all(): every screen line of ONE Short in ONE voice (never a mix line by line), each line checked by ear.
Output: mono 44.1 kHz wav.
"""
import difflib
import os
import re
import shutil
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
# 10 Nov 2026: 400 "Unknown name speechConfig" = google-genai 3.x talks to API v1 by default (fixed: v1beta in
# _gemini). The 2.5 models (the voice of every earlier Short) stay first; Gemini 3.8 TTS through the Interactions
# API (client.interactions.create, same prebuilt voices incl. Achird) is the fallback.
MODELS = [m for m in [os.getenv("TTS_MODEL", ""), *(_F.get("tts_models") or []),
                      "gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts",
                      "gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-3.1-flash-tts-preview"] if m]
MODELS = list(dict.fromkeys(MODELS))  # no duplicates

_DAY_OUT = set()  # Gemini TTS models whose DAILY quota is used up in this run
MAX_WAIT = 150  # max seconds per line spent waiting out the per-minute limit
_DEAD = set()  # providers that are out of quota / blocked for this run


def _pcm_to_wav(pcm: bytes, path: Path, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def _quota_kind(msg):
    """'day' = the DAILY free quota of this model is used up (back tomorrow); 'minute' = only the per-minute
    rate limit was hit (back in seconds - wait, do NOT switch voice)."""
    m = str(msg).lower().replace("_", "")
    return "day" if ("perday" in m or "daily" in m) else "minute"


def _retry_after(msg, default=20.0):
    """Seconds Gemini asks us to wait ('retryDelay': '37s' / 'Please retry in 36.2s')."""
    m = re.search(r"retry\w*[\"':\s]+([\d.]+)\s*s", str(msg), re.I) or re.search(r"retry in ([\d.]+)", str(msg), re.I)
    return min(float(m.group(1)) + 1.0, 65.0) if m else default


def _interactions_model(model):
    return model.startswith(("gemini-3.8", "gemini-3.1")) and model.endswith(("-tts", "-tts-preview"))


def _gemini_interactions(client, model, text, raw: Path):
    """Gemini 3.x TTS (Interactions API): the verbatim line in "input", the delivery style as a speech_metadata
    annotation (so the style is never read aloud), the prebuilt voice in generation_config.speech_config.
    Unary answer = audio/wav (RIFF, 24 kHz mono 16-bit), base64 in interaction.output_audio.data."""
    import base64
    it = client.interactions.create(
        model=model,
        input=[{"type": "user_input",
                "content": [{"type": "text", "text": text,
                             "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": VOICE}]})
    audio = getattr(it, "output_audio", None)
    data = getattr(audio, "data", None) if audio is not None else None
    if isinstance(data, str):
        data = base64.b64decode(data)
    if not data or len(data) < 4800:  # < 0.1 s of audio = nothing usable came back
        raise RuntimeError("Gemini returned no audio")
    if data[:4] == b"RIFF":
        raw.write_bytes(data)
    else:  # headerless 16-bit PCM (older default) -> wrap it
        _pcm_to_wav(data, raw, 24000)


def _gemini(text, raw: Path):
    from google import genai
    from google.genai import types
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY missing")
    # google-genai 3.x defaults to API "v1", which has no speechConfig (-> 400 "Unknown name speechConfig" since
    # ~Nov 2026). TTS lives in v1beta.
    client = genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(api_version="v1beta"))
    models = [m for m in MODELS if m not in _DAY_OUT]
    last, waited, attempt = None, 0.0, 0
    while models and attempt < 8:
        model = models[attempt % len(models)]
        attempt += 1
        try:
            if _interactions_model(model):
                _gemini_interactions(client, model, text, raw)
                return
            r = client.models.generate_content(
                model=model, contents=f"{STYLE}: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)))))
            part = r.candidates[0].content.parts[0]
            data = part.inline_data.data
            if not data or len(data) < 4800:  # < 0.1 s of audio = nothing usable came back
                raise RuntimeError("Gemini returned no audio")
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
            print(f"[tts] {model} attempt {attempt} failed: {msg[:160]}")
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                if _quota_kind(msg) == "day":  # this model's DAILY quota is gone -> try the next model
                    _DAY_OUT.add(model)
                    models = [m for m in models if m != model]
                    continue
                wait = _retry_after(msg)  # only the per-minute limit -> wait it out, keep the same voice
                if waited + wait > MAX_WAIT:
                    break
                print(f"[tts] per-minute limit (quota NOT used up) - waiting {wait:.0f}s")
                waited += wait
                time.sleep(wait)
                continue
            if "404" in msg or "NOT_FOUND" in msg:  # this model name is not available -> drop it
                models = [m for m in models if m != model]
                continue
            time.sleep(min(4 * attempt, 20))  # 500 / 503 / timeout: short pause, try again
    if not models:  # every Gemini TTS model is out of DAILY quota -> backup voice for the rest of this run
        _DEAD.add("gemini")
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


def speak(text, out_wav: Path, rate=44100, only=None):
    """text -> out_wav (mono, `rate` Hz), leading/trailing silence trimmed. Returns the length in seconds.
    only = use just this provider (speak_all keeps ONE voice for a whole Short)."""
    raw = out_wav.with_suffix(".raw.wav")
    errors = []
    for name, fn in (("gemini", _gemini), ("edge", _edge), ("piper", _piper)):
        if name in _DEAD or (only and name != only):
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
        raise RuntimeError("all TTS providers failed: " + " | ".join(errors or [f"{only} is not available in this run"]))
    # trim silence at both ends, resample
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ac", "1", "-ar", str(rate),
                    "-c:a", "pcm_s16le", str(out_wav)], check=True)
    raw.unlink(missing_ok=True)
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(out_wav)], capture_output=True, text=True, check=True).stdout.strip())


def _says(wav: Path, text):
    """0-1: how well the audio says `text` (whisper). Catches Gemini reading the style instruction aloud,
    cut-off endings and garbled words."""
    from . import editor
    wd = wav.parent / f"chk_{wav.stem}"
    wd.mkdir(parents=True, exist_ok=True)
    try:
        heard = " ".join(w for _, _, w in editor.transcribe(wav, wd))
    except Exception as e:
        print(f"[tts] speech check skipped: {str(e)[:120]}")
        return 1.0
    finally:
        shutil.rmtree(wd, ignore_errors=True)

    def norm(s):
        return re.findall(r"[a-z0-9]+", s.lower())
    return difflib.SequenceMatcher(None, norm(heard), norm(text)).ratio()


def speak_all(texts, outs, rate=44100, order=("gemini", "edge", "piper")):
    """Every screen line of ONE Short in ONE voice. Gemini first (the same voice as your Flow avatar). Only if
    Gemini is really out (daily quota used up / down) are ALL lines re-voiced with the next provider - a Short
    never mixes voices line by line. Every line is checked by ear (whisper); a badly spoken line is made again.
    Returns the provider used: "gemini" | "edge" | "piper"."""
    errors = []
    for name in order:
        if name in _DEAD:
            continue
        try:
            for t, o in zip(texts, outs):
                score = 0.0
                for _ in range(2):
                    speak(t, o, rate, only=name)
                    score = _says(o, t)
                    if score >= 0.7:
                        break
                    print(f"[tts] {name} said the line badly (match {score:.2f}) -> again: {t[:60]}")
                if score < 0.5 and name != "piper":
                    raise RuntimeError(f"{name} cannot say this line correctly (match {score:.2f}): {t[:60]}")
            if name != "gemini":
                print(f"[tts] Gemini TTS unavailable -> ALL screen lines in the backup voice '{name}'")
            return name
        except Exception as e:
            errors.append(f"{name}: {str(e)[:160]}")
            print(f"[tts] {name} could not voice the whole Short -> next provider ({str(e)[:160]})")
    raise RuntimeError("no TTS provider could voice the Short: " + " | ".join(errors))
