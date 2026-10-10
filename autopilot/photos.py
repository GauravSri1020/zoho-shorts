"""Photo agent: keeps your avatar photos fresh (new scenes, same face), so videos never look the same.

Once a week it asks Gemini's image model for new photorealistic photos of you, using your real photos as
reference (city at night with lights, office, cafe, street...). A separate QA agent compares each new photo
with your real ones and rejects anything that is not clearly you, looks fake, has a hidden/turned face
(lip-sync needs a clear face), extra fingers, text or logos. Approved photos are added to the encrypted
bundle (assets/avatars.enc) and join the rotation. Your original photos are never removed.
These are synthetic images of you, so videos keep YouTube's AI label on (they already do).
"""
import io
import json
import os
import random
import subprocess
import tarfile
import time
from pathlib import Path

from google.genai import types
from PIL import Image

from .config import ASSETS_DIR, CH
from . import writer

_P = CH.get("photo_agent", {})
IMAGE_MODELS = [m.strip() for m in os.getenv("GEMINI_IMAGE_MODELS", ",".join(_P.get("models", [
    "gemini-2.5-flash-image", "gemini-2.5-flash-image-preview"]))).split(",") if m.strip()]
PER_RUN = int(_P.get("per_run", 2))
MAX_GENERATED = int(_P.get("max_generated", 18))
SCENES = _P.get("scenes", [
    "walking slowly on a city street at night, warm string lights and shop lights glowing behind, bokeh",
    "standing on a rooftop terrace at dusk with fairy lights behind",
    "in a modern office with glass walls, people working in the blurred background",
    "sitting at a cafe table with a laptop, warm evening light",
    "walking in a co-working space corridor, soft daylight",
    "standing near a window with city lights at night behind",
])
ENC = ASSETS_DIR / "avatars.enc"


def _key():
    k = os.getenv("AVATAR_KEY", "").strip()
    if not k:
        raise RuntimeError("AVATAR_KEY secret missing")
    return k


def unpack():
    """{name: jpeg bytes} from the encrypted bundle."""
    dec = subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-in", str(ENC), "-pass", "env:AVATAR_KEY"],
                         capture_output=True, check=True, env={**os.environ, "AVATAR_KEY": _key()}).stdout
    with tarfile.open(fileobj=io.BytesIO(dec)) as t:
        return {m.name: t.extractfile(m).read() for m in t.getmembers() if m.isfile()}


def pack(photos):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        for name in sorted(photos):
            info = tarfile.TarInfo(name)
            info.size = len(photos[name])
            t.addfile(info, io.BytesIO(photos[name]))
    subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-out", str(ENC), "-pass", "env:AVATAR_KEY"],
                   input=buf.getvalue(), check=True, env={**os.environ, "AVATAR_KEY": _key()})


def _generate(refs, scene):
    client = writer._gemini()
    prompt = (f"Create a new photorealistic vertical (9:16) photo of the SAME man shown in these reference photos: "
              f"same face, beard, hair, skin tone and body build. Scene: {scene}. He faces the camera, face clearly "
              "visible and well lit, head and upper body in frame, mouth closed, natural relaxed expression, "
              "smart casual clothes. Shot on a phone camera, natural colours. No text, no logos, no watermark, "
              "no alcohol, no other person in focus.")
    last = None
    for model in IMAGE_MODELS:
        try:
            cfg = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
            r = client.models.generate_content(model=model, contents=[*refs, prompt], config=cfg)
            for part in r.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    return part.inline_data.data, model
            last = RuntimeError("no image in response")
        except Exception as e:
            last = e
            print(f"[photos] {model} failed: {str(e)[:200]}")
            time.sleep(5)
    raise RuntimeError(f"image model unavailable: {last}")


def _qa(refs, candidate):
    client = writer._gemini()
    prompt = """You check a generated photo before it is used as the face of a YouTube presenter.
The first images are REAL photos of the person. The LAST image is the generated candidate.
Approve only if ALL are true: clearly the same person; photorealistic (not cartoon/plastic/over-smoothed);
face frontal or near-frontal, sharp and unobstructed (needed for lip-sync); normal hands/fingers; no text,
logos or watermarks; nothing embarrassing, offensive or alcohol-related.
Return JSON: {"approved": true|false, "same_person": 1-10, "realism": 1-10, "issues": ["..."]}"""
    for model in writer._MODELS:
        try:
            r = client.models.generate_content(
                model=model, contents=[*refs, candidate, prompt],
                config=types.GenerateContentConfig(temperature=0.1, response_mime_type="application/json"))
            out = json.loads(r.text)
            ok = bool(out.get("approved")) and int(out.get("same_person") or 0) >= 8 and int(out.get("realism") or 0) >= 7
            return ok, out
        except Exception as e:
            print(f"[photos] QA via {model} failed: {str(e)[:160]}")
            time.sleep(5)
    raise RuntimeError("photo QA agent unavailable")


def run(st):
    """Adds up to PER_RUN approved new photos. Returns number added."""
    photos = unpack()
    originals = {k: v for k, v in photos.items() if not k.startswith("gen_")}
    refs = [Image.open(io.BytesIO(b)).convert("RGB") for b in list(originals.values())[:3]]
    used = st.setdefault("photo_scenes", [])
    scenes = [s for s in SCENES if s not in used[-len(SCENES) + 1:]] or SCENES
    added = 0
    for attempt in range(PER_RUN * 3):
        if added >= PER_RUN:
            break
        scene = random.choice(scenes)
        data, model = _generate(refs, scene)
        cand = Image.open(io.BytesIO(data)).convert("RGB")
        ok, verdict = _qa(refs, cand)
        print(f"[photos] '{scene[:40]}...' via {model}: approved={ok} {verdict}")
        if not ok:
            continue
        b = io.BytesIO()
        cand.save(b, "JPEG", quality=90)
        name = f"gen_{time.strftime('%Y%m%d%H%M%S')}_{attempt}.jpg"
        photos[name] = b.getvalue()
        used.append(scene)
        added += 1
    generated = sorted(k for k in photos if k.startswith("gen_"))
    for old in generated[:-MAX_GENERATED]:              # keep the bundle small, originals always stay
        photos.pop(old)
    if added:
        pack(photos)
    print(f"[photos] {added} new photo(s) added, {len(photos)} in rotation")
    return added
