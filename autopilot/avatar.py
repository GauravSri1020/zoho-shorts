"""The talking avatar, made from YOUR photo (synthetic media -> uploaded with YouTube's AI label on).

Engine 1 (lip-sync): SadTalker, open source, runs free on the GitHub runner's CPU (installed by
tools/install_sadtalker.sh, ~20-40 min per Short). Engine 2 (backup): your photo with slow camera motion,
so a Short is still published if the lip-sync engine fails.

Your photos are rotated: every Short uses a different one. They sit in the repo only as an encrypted bundle
(assets/avatars.enc); the AVATAR_KEY GitHub secret unlocks them during the run.
"""
import base64
import os
import subprocess
from pathlib import Path

from PIL import Image

from .config import ASSETS_DIR, CH

SADTALKER_DIR = Path(os.getenv("SADTALKER_DIR") or Path.home() / "sadtalker")
_A = CH.get("avatar", {})
ENGINE = os.getenv("AVATAR_ENGINE") or _A.get("engine", "sadtalker")   # sadtalker | photo
FPS = 30


def _all_photos(workdir: Path):
    """Your photos, in order. Sources (first that works):
    1. assets/avatars.enc  - encrypted photo bundle in the repo, unlocked with the AVATAR_KEY secret
    2. AVATAR_PHOTO_B64    - one photo as a secret
    3. assets/avatars/*.jpg or assets/avatar.jpg - when running on your own computer
    """
    src = workdir / "photos"
    src.mkdir(parents=True, exist_ok=True)
    enc, key = ASSETS_DIR / "avatars.enc", os.getenv("AVATAR_KEY", "").strip()
    if enc.exists() and key:
        dec = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-in", str(enc),
                              "-pass", "env:AVATAR_KEY"], capture_output=True, check=True,
                             env={**os.environ, "AVATAR_KEY": key}).stdout
        subprocess.run(["tar", "xf", "-", "-C", str(src)], input=dec, check=True)
    elif os.getenv("AVATAR_PHOTO_B64", "").strip():
        (src / "1.jpg").write_bytes(base64.b64decode(os.environ["AVATAR_PHOTO_B64"].strip()))
    else:
        for p in list((ASSETS_DIR / "avatars").glob("*.jp*g")) + [ASSETS_DIR / "avatar.jpg"]:
            if p.exists():
                (src / p.name).write_bytes(p.read_bytes())
    photos = sorted(src.glob("*.jp*g"))
    if not photos:
        raise RuntimeError("no avatar photo: set the AVATAR_KEY secret (see SETUP.md)")
    return photos


def photo(workdir: Path, last_used=None):
    """Picks the next photo in rotation (never the same as last time). Returns (path, name)."""
    photos = _all_photos(workdir)
    names = [p.name for p in photos]
    i = (names.index(last_used) + 1) % len(photos) if last_used in names else 0
    im = Image.open(photos[i]).convert("RGB")
    if im.width < 1080:                    # small WhatsApp photos -> upscale once, it looks cleaner full screen
        im = im.resize((1080, int(1080 * im.height / im.width)), Image.LANCZOS)
    out = workdir / "avatar.jpg"
    im.save(out, quality=95)
    print(f"[avatar] photo {names[i]} ({i + 1}/{len(photos)})")
    return out, names[i]


def sadtalker_ready():
    return (SADTALKER_DIR / ".ok").exists() and (SADTALKER_DIR / "venv" / "bin" / "python").exists()


def _sadtalker(img, audio, workdir):
    res = workdir / "sadtalker"
    res.mkdir(parents=True, exist_ok=True)
    cmd = [str(SADTALKER_DIR / "venv" / "bin" / "python"), "inference.py", "--driven_audio", str(Path(audio).resolve()),
           "--source_image", str(Path(img).resolve()), "--result_dir", str(res.resolve()),
           "--still", "--preprocess", "full", "--size", "256", "--expression_scale", "1.0", "--cpu"]
    print("[avatar] SadTalker running (CPU, this takes a while)...")
    subprocess.run(cmd, check=True, cwd=SADTALKER_DIR, timeout=3 * 3600)
    vids = sorted(res.rglob("*.mp4"), key=lambda p: p.stat().st_mtime)
    if not vids:
        raise RuntimeError("SadTalker produced no video")
    return vids[-1]


def _photo_motion(img, dur, out):
    """Backup without lip-sync: your photo as video (the editor adds the camera movement)."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(img), "-t", f"{dur:.3f}",
                    "-vf", f"scale=trunc(iw/2)*2:trunc(ih/2)*2,fps={FPS},format=yuv420p",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", str(out)], check=True)
    return out


def make(audio, dur, workdir: Path, force_photo=False, last_photo=None):
    """Returns (avatar video path, engine name, photo name)."""
    img, name = photo(workdir, last_photo)
    if not force_photo and ENGINE == "sadtalker":
        if sadtalker_ready():
            try:
                return _sadtalker(img, audio, workdir), "sadtalker", name
            except Exception as e:
                print(f"[avatar] SadTalker failed, using photo motion: {str(e)[:300]}")
        else:
            print("[avatar] SadTalker not installed, using photo motion")
    return _photo_motion(img, dur, workdir / "avatar_photo.mp4"), "photo", name
