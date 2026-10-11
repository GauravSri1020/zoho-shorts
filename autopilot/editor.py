"""Video editor for the fully automatic Shorts.

- word-by-word captions timed on the actual voice (faster-whisper, free, runs on GitHub), Roman Hinglish
- full screen avatar on its real photo background, slow "handheld camera" movement (different every video)
- no cards, no badge, no split screen: only the spoken words as captions
- technical checks (sound, black frames, size) before the QA agent watches it
"""
import bisect
import json
import re
import shutil
import subprocess
from pathlib import Path


from .config import (ASSETS_DIR, BADGE, CAPTION_MAX_WORDS, MAX_VIDEO_SECONDS, ROMAN_CAPTIONS, WHISPER_LANGUAGE,
                     WHISPER_MODEL)

W, H, FPS = 1080, 1920, 30
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def _run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


# ------------------------------------------------------------------ probing
def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format",
                          str(path)], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    if not v:
        return None
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = rot or int(float(v.get("tags", {}).get("rotate", 0) or 0))
    if abs(rot) % 180 == 90:
        w, h = h, w
    return {"width": w, "height": h, "portrait": h > w,
            "duration": float(data["format"].get("duration") or v.get("duration") or 0),
            "audio": any(s.get("codec_type") == "audio" for s in data["streams"])}


# ------------------------------------------------------------------ transcription
def transcribe(video, workdir):
    """Returns [(start, end, word)] from your own voice."""
    from faster_whisper import WhisperModel
    wav = workdir / "voice16k.wav"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(wav), language=WHISPER_LANGUAGE, word_timestamps=True,
                                      vad_filter=True, beam_size=5)
    words = []
    for seg in segments:
        for w in seg.words or []:
            t = w.word.strip()
            if t:
                words.append((float(w.start), float(w.end), t))
    print(f"[editor] whisper: {len(words)} words, language={info.language}")
    return words


def romanize_if_needed(words):
    if not (ROMAN_CAPTIONS and any(DEVANAGARI.search(w) for _, _, w in words)):
        return words
    from . import writer
    roman = writer.romanize_words([w for _, _, w in words])
    if not roman:
        return words
    return [(s, e, r) for (s, e, _), r in zip(words, roman)]


def align_to_script(words, script_text, audio=None):
    """Script words with timings: [(start, end, word)].

    Uses whisper's word timings when they look sane. When they don't (whisper on Hinglish TTS sometimes
    returns one 9 s word or squeezes 20 words into half a second), the script is spread over the real
    speech parts of the audio (silence detection), each word's share proportional to its length.
    """
    sw = (script_text or "").split()
    if not sw:
        return words
    out = _align_whisper(words, script_text) if words else []
    if out and _timings_sane(out):
        return out
    if audio is not None:
        spans = speech_spans(audio)
    elif words:
        spans = [(words[0][0], words[-1][1])]
    else:
        return words
    print(f"[editor] whisper timings unusable -> script spread over {len(spans)} speech parts of the audio")
    return _spread(sw, spans)


def _timings_sane(aligned):
    """False if any word is absurdly long, or many words are absurdly short."""
    too_long = sum(e - s > max(1.6, 0.22 * len(w)) for s, e, w in aligned)
    too_short = sum(e - s < 0.07 for s, e, _ in aligned)
    return too_long == 0 and too_short <= 0.2 * len(aligned)


def speech_spans(audio, noise="-35dB", min_silence=0.18):
    """[(start, end)] of the parts of the audio where someone is speaking."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(audio)], capture_output=True, text=True, check=True).stdout)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(audio), "-af",
                          f"silencedetect=noise={noise}:d={min_silence}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [max(float(x), 0.0) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    ends += [dur] * (len(starts) - len(ends))
    spans, t = [], 0.0
    for s, e in zip(starts, ends):
        if s - t > 0.05:
            spans.append((t, s))
        t = e
    if dur - t > 0.05:
        spans.append((t, dur))
    return spans or [(0.0, dur)]


def _spread(script_words, spans):
    """Lays the script words over the speech spans; a word's share of speech time ~ its length."""
    cum = [0.0]
    for s, e in spans:
        cum.append(cum[-1] + e - s)
    speech = cum[-1]

    def real_time(x):                       # x seconds into the speech -> time in the audio
        k = min(max(bisect.bisect_right(cum, x) - 1, 0), len(spans) - 1)
        return spans[k][0] + min(x - cum[k], spans[k][1] - spans[k][0])

    lens = [len(w) + 1 for w in script_words]
    total, acc, out = sum(lens), 0, []
    for w, l in zip(script_words, lens):
        a = real_time(acc / total * speech)
        acc += l
        b = real_time(acc / total * speech - 1e-6)
        out.append((a, max(b, a + 0.05), w))
    return out


def _align_whisper(words, script_text):
    """Captions = the exact script words (Roman Hinglish), timed on whisper's word timings.

    Whisper on Hinglish audio often returns Devanagari / mis-heard words, and romanizing needs Gemini
    (often out of quota). We already KNOW what was said, so only the timing is taken from whisper.
    """
    sw = (script_text or "").split()
    if not words or not sw:
        return words
    wl = [max(len(w), 1) for _, _, w in words]
    cum = [0]
    for x in wl:
        cum.append(cum[-1] + x)
    total = cum[-1]

    def t_at(f):
        pos = min(max(f, 0.0), 1.0) * total
        k = min(max(bisect.bisect_right(cum, pos) - 1, 0), len(words) - 1)
        s, e, _ = words[k]
        return s + (e - s) * min(max((pos - cum[k]) / wl[k], 0.0), 1.0)

    sl = [max(len(w), 1) for w in sw]
    stotal, acc, out = sum(sl), 0, []
    for w, l in zip(sw, sl):
        a = t_at(acc / stotal)
        acc += l
        b = t_at(acc / stotal - 1e-9)
        out.append((a, max(b, a + 0.05), w))
    return out


# ------------------------------------------------------------------ captions (ASS)
def chunks(words, max_words=CAPTION_MAX_WORDS, max_chars=20, pause=0.35):
    out, cur = [], []
    for wd in words:
        if cur and (len(cur) >= max_words or len(" ".join(x[2] for x in cur + [wd])) > max_chars
                    or wd[0] - cur[-1][1] > pause or re.search(r"[.?!,।]$", cur[-1][2])):
            out.append(cur)
            cur = []
        cur.append(wd)
    if cur:
        out.append(cur)
    return out


def _ts(t):
    t = max(t, 0)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def build_ass(words, hook, duration, split, path):
    yellow, white = r"{\c&H000AD6FF&}", r"{\c&H00FFFFFF&}"
    cap_margin = 330 if split else 560
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Poppins,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,{cap_margin},1
Style: Hook,Poppins,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,3,8,70,70,120,1
Style: Badge,Poppins,36,&H001A0A08,&H001A0A08,&H00A02EFF,&H00A02EFF,-1,0,0,0,100,100,1,0,3,12,0,9,50,50,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if BADGE:
        ev.append(f"Dialogue: 2,{_ts(0)},{_ts(duration)},Badge,,0,0,0,,{_esc(BADGE.upper())}")
    if hook:
        ev.append(f"Dialogue: 2,{_ts(0)},{_ts(duration)},Hook,,0,0,0,,{_esc(hook.upper())}")
    groups = chunks(words)
    for gi, g in enumerate(groups):
        nxt = groups[gi + 1][0][0] if gi + 1 < len(groups) else duration
        g_end = nxt if nxt - g[-1][1] < 0.6 else g[-1][1] + 0.25
        for i, (s, e, _) in enumerate(g):
            start = g[0][0] if i == 0 else s
            end = g[i + 1][0] if i + 1 < len(g) else g_end
            if end <= start:
                continue
            parts = [(yellow + _esc(w) + white) if j == i else _esc(w) for j, (_, _, w) in enumerate(g)]
            pop = r"{\fscx112\fscy112\t(0,90,\fscx100\fscy100)}" if i == 0 else ""
            ev.append(f"Dialogue: 1,{_ts(start)},{_ts(min(end, duration))},Cap,,0,0,0,,{pop}{' '.join(parts)}")
    path.write_text(header + "\n".join(ev) + "\n", encoding="utf-8")
    return path


# ------------------------------------------------------------------ automatic checks (no human review)
def check_media(path):
    """Cheap technical checks on the finished file. Returns a list of problems (empty = ok)."""
    problems = []
    info = probe(path)
    if not info or (info["width"], info["height"]) != (W, H):
        problems.append("wrong resolution")
    if not info or not info["audio"]:
        return problems + ["no audio track"]
    if info["duration"] < 8:
        problems.append(f"too short ({info['duration']:.1f}s)")
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf", "blackdetect=d=1.0:pix_th=0.08",
                          "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", err)
    if m and float(m.group(1)) < -40:
        problems.append(f"audio almost silent ({m.group(1)} dB)")
    black = sum(float(x) for x in re.findall(r"black_duration:([\d.]+)", err))
    if black > 1.5:
        problems.append(f"{black:.1f}s of black video")
    return problems


# ------------------------------------------------------------------ full-screen layout (fully automatic Shorts)
def _motion(rng, dur):
    """A different slow 'handheld camera' move every video: gentle push-in + drift + small sway."""
    n = max(int(dur * FPS), 1)
    sx, sy = rng.choice((-1, 1)), rng.choice((-1, 1))
    z0, dz = rng.uniform(1.03, 1.07), rng.uniform(0.08, 0.15) / n      # total zoom over the video
    drift = rng.uniform(60, 140) / n                                      # total sideways drift in px
    return (f"zoompan=z='{z0:.3f}+{dz:.7f}*on':"
            f"x='iw/2-iw/zoom/2+{sx}*(on*{drift:.5f}+sin(on/37)*10)':"
            f"y='ih*0.42-ih/zoom*0.42+{sy}*cos(on/53)*8':d=1:s={W}x{H}:fps={FPS}")


def render_fullscreen(avatar_mp4, voice_wav, words, workdir: Path, out_path: Path, rng=None):
    """Your avatar full screen (real background, lights etc.) with a moving camera; only the spoken words
    appear as big captions. Returns (path, duration)."""
    import random
    rng = rng or random.Random()
    workdir.mkdir(parents=True, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(voice_wav)], capture_output=True, text=True, check=True).stdout)
    dur = min(dur, MAX_VIDEO_SECONDS)
    shutil.copytree(ASSETS_DIR / "fonts", workdir / "fonts", dirs_exist_ok=True)
    build_ass(words, "", dur, False, workdir / "captions.ass")
    # whole photo visible (face never cut off), the same scene blurred behind it fills the 9:16 frame
    fc = (f"[0:v]fps={FPS},tpad=stop_mode=clone:stop_duration={dur:.3f},split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,"
          f"eq=brightness=-0.08,setsar=1[bg];"
          f"[b]scale={W + 80}:{H - 520}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2-140,{_motion(rng, dur)},"
          f"eq=contrast=1.04:saturation=1.08,vignette=PI/6,trim=duration={dur:.3f},format=yuv420p,"
          f"subtitles=captions.ass:fontsdir=fonts[v];[1:a]anull[va]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(Path(avatar_mp4).resolve()),
           "-i", str(Path(voice_wav).resolve())]
    bgm = ASSETS_DIR / "bgm.mp3"
    if bgm.exists():
        cmd += ["-stream_loop", "-1", "-i", str(bgm)]
        fc += ";[2:a]volume=0.06,aresample=44100[m];[va][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]"
    else:
        fc += ";[va]anull[a]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
            "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out_path.resolve())]
    _run(cmd, cwd=workdir)
    print(f"[editor] full-screen Short rendered {out_path} ({dur:.1f}s)")
    return out_path, dur
