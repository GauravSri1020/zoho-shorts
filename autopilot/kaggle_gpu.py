"""Kaggle GPU avatar engine: your talking clip, lip-synced to the AI voice on Kaggle's free GPU.

    channel.yaml -> avatar.engine: "kaggle"

How it works (fully automatic, ~15-25 min per Short, free: Kaggle gives ~30 GPU hours a week):
1. A short real-looking clip of you talking (assets/base_clips/*.mp4, rotated) + the Short's voice are uploaded
   as a PRIVATE Kaggle dataset (<user>/gsx-lipsync-input).
2. A private Kaggle notebook (<user>/gsx-lipsync, code: kaggle_kernel/lipsync.py) runs LatentSync 1.5 on a
   T4 GPU: the clip is looped to the voice length and the lips are redrawn to match the voice.
3. The result comes back to GitHub and goes into composer.py exactly like the other engines.

Secrets: KAGGLE_USERNAME, KAGGLE_API_TOKEN (Kaggle -> Settings -> API Tokens). Phone-verified Kaggle account
(needed for GPU + internet). If anything fails, avatar.py falls back to SadTalker, then the photo.

Test on its own:  python -m autopilot.kaggle_gpu test   (makes out/gputest/avatar_kaggle.mp4)
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .config import ASSETS_DIR, CH, OUT_DIR

_K = (CH.get("avatar", {}) or {}).get("kaggle", {}) or {}
DATASET_SLUG = _K.get("dataset", "gsx-lipsync-input")
KERNEL_SLUG = _K.get("kernel", "gsx-lipsync")
MACHINE = _K.get("machine", "NvidiaTeslaT4")
TIMEOUT_MIN = int(_K.get("timeout_minutes", 90))
KERNEL_SRC = Path(__file__).parent / "kaggle_kernel" / "lipsync.py"


def _user():
    """Kaggle username; also accepts a pasted profile link like https://www.kaggle.com/<name>."""
    u = os.getenv("KAGGLE_USERNAME", "").strip().rstrip("/").split("/")[-1].lstrip("@").strip()
    if not u or not (os.getenv("KAGGLE_API_TOKEN") or os.getenv("KAGGLE_KEY")):
        raise RuntimeError("KAGGLE_USERNAME / KAGGLE_API_TOKEN secrets not set")
    os.environ["KAGGLE_USERNAME"] = u
    return u


def _kaggle(*args, check=True, timeout=600):
    p = subprocess.run(["kaggle", *args], capture_output=True, text=True, timeout=timeout)
    out = (p.stdout or "") + (p.stderr or "")
    if check and p.returncode != 0:
        raise RuntimeError(f"kaggle {' '.join(args[:2])} failed: {out.strip()[-500:]}")
    return out


def _run(cmd):
    subprocess.run(cmd, check=True)


# ------------------------------------------------------------------ inputs
def base_clip(last=None):
    """Next base clip in rotation (never the same as last time). Returns path."""
    clips = sorted((ASSETS_DIR / "base_clips").glob("*.mp4"))
    if not clips:
        raise RuntimeError("no base clip in assets/base_clips/")
    names = [c.name for c in clips]
    i = (names.index(last) + 1) % len(clips) if last in names else 0
    return clips[i]


def _upload_inputs(user, base, audio, run_id, workdir: Path):
    d = workdir / "kaggle_dataset"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(base), "-an", "-r", "25", "-c:v", "libx264",
          "-crf", "16", "-pix_fmt", "yuv420p", str(d / "base.mp4")])
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio), "-ac", "1", "-ar", "16000", str(d / "audio.wav")])
    (d / "run.txt").write_text(run_id)
    (d / "dataset-metadata.json").write_text(json.dumps({
        "title": DATASET_SLUG, "id": f"{user}/{DATASET_SLUG}", "licenses": [{"name": "CC0-1.0"}]}))
    exists = "ready" in _kaggle("datasets", "status", f"{user}/{DATASET_SLUG}", check=False).lower()
    if exists:
        out = _kaggle("datasets", "version", "-p", str(d), "-m", run_id, "--dir-mode", "skip")
    else:
        out = _kaggle("datasets", "create", "-p", str(d))  # private by default
    print(f"[kaggle] dataset {'version' if exists else 'create'}: {out.strip()[-300:]}")
    if "error" in out.lower() or "invalid" in out.lower():
        raise RuntimeError(f"Kaggle dataset upload failed: {out.strip()[-300:]}")
    for _ in range(60):                                   # wait until Kaggle has processed the new version
        time.sleep(10)
        if "ready" in _kaggle("datasets", "status", f"{user}/{DATASET_SLUG}", check=False).lower():
            break
    else:
        raise RuntimeError("Kaggle dataset never became ready")
    print(f"[kaggle] inputs uploaded ({'new version' if exists else 'new dataset'}), run {run_id}")


def _push_kernel(user, workdir: Path, machine=MACHINE):
    d = workdir / "kaggle_kernel"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    shutil.copy(KERNEL_SRC, d / "lipsync.py")
    meta = {"id": f"{user}/{KERNEL_SLUG}", "title": KERNEL_SLUG, "code_file": "lipsync.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
            "dataset_sources": [f"{user}/{DATASET_SLUG}"], "competition_sources": [], "kernel_sources": []}
    if machine:
        meta["machine_shape"] = machine
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1))
    out = _kaggle("kernels", "push", "-p", str(d), check=False)
    print(f"[kaggle] push: {out.strip()[-300:]}")
    if "successfully pushed" in out.lower():
        return
    if machine:
        print("[kaggle] retrying without machine_shape")
        return _push_kernel(user, workdir, machine=None)
    raise RuntimeError(f"Kaggle notebook push failed: {out.strip()[-300:]}")


def _fetch_output(user, workdir: Path):
    out = workdir / "kaggle_out"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    _kaggle("kernels", "output", f"{user}/{KERNEL_SLUG}", "-p", str(out), "--force", check=False, timeout=900)
    read = lambda n: (out / n).read_text(errors="ignore").strip() if (out / n).exists() else ""
    return out, read("run.txt"), read("status.txt")


def _run_on_gpu(user, run_id, workdir: Path):
    """Pushes the notebook and waits until THIS run's output is back. Returns the output folder."""
    t_end = time.time() + TIMEOUT_MIN * 60
    for attempt in (1, 2):
        _push_kernel(user, workdir)
        print(f"[kaggle] GPU notebook started (attempt {attempt}), waiting - usually 15-25 min...")
        time.sleep(90)                                   # let Kaggle switch from the previous run's status
        while time.time() < t_end:
            status = _kaggle("kernels", "status", f"{user}/{KERNEL_SLUG}", check=False).lower()
            if any(s in status for s in ("complete", "error", "cancel")):
                out, got, st = _fetch_output(user, workdir)
                if got == run_id:
                    print(f"[kaggle] finished: {status.strip()[-120:]}")
                    return out, st or f"no status.txt ({status.strip()[-150:]})"
                if got and got != run_id and attempt == 1 and "complete" in status:
                    print(f"[kaggle] output is from an older run ({got}); the dataset was not ready - retrying")
                    time.sleep(60)
                    break
                if "error" in status or "cancel" in status:
                    return out, st or f"notebook {status.strip()[-200:]}"
            time.sleep(30)
        else:
            raise RuntimeError(f"Kaggle GPU run timed out after {TIMEOUT_MIN} min")
    raise RuntimeError("Kaggle kept returning an older run's output")


def make(audio, workdir: Path, last_clip=None):
    """Lip-synced avatar video (length = voice). Returns (mp4 path, base clip name)."""
    user = _user()
    workdir.mkdir(parents=True, exist_ok=True)
    base = base_clip(last_clip)
    run_id = f"{os.getenv('GITHUB_RUN_ID', 'local')}-{int(time.time())}"
    _upload_inputs(user, base, audio, run_id, workdir)
    out, st = _run_on_gpu(user, run_id, workdir)
    if (out / "log.txt").exists():
        print("[kaggle] notebook log (end):\n" + (out / "log.txt").read_text(errors="ignore")[-2500:])
    if st != "ok" or not (out / "result.mp4").exists():
        raise RuntimeError(f"Kaggle lip-sync failed: {st[:300]}")
    res = workdir / "avatar_kaggle.mp4"
    shutil.move(str(out / "result.mp4"), res)
    print(f"[kaggle] lip-synced avatar ready: {res} (base clip {base.name})")
    return res, base.name


def self_test():
    """Stand-alone check: edge-tts line -> Kaggle lip-sync -> out/gputest/avatar_kaggle.mp4"""
    work = OUT_DIR / "gputest"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    text = ("Namaste! Zoho Books me har mahine report ke filters baar baar set karna band karo. "
            "Aaj main aapko ek simple tarika dikhata hoon jo do minute me sab fix kar dega.")
    mp3 = work / "voice.mp3"
    _run([sys.executable, "-m", "edge_tts", "--voice", "hi-IN-MadhurNeural", "--text", text,
          "--write-media", str(mp3)])
    wav = work / "voice.wav"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "24000", str(wav)])
    res, _ = make(wav, work)
    final = work / "short.mp4"                            # same name the workflow keeps as an artifact
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(res), "-i", str(wav), "-map", "0:v", "-map", "1:a",
          "-c:v", "copy", "-c:a", "aac", "-shortest", str(final)])
    print(f"[kaggle] TEST OK -> {final}")


if __name__ == "__main__":
    if sys.argv[1:] == ["test"]:
        self_test()
    else:
        print(__doc__)
