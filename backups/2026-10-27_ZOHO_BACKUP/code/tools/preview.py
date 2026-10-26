"""Make one Short on your own computer without uploading (to check the look).

  pip install -r requirements.txt     (and install ffmpeg)
  export GEMINI_API_KEY=...            (needed for the script and the voice)
  set AVATAR_KEY (unlocks assets/avatars.enc) or put photos in assets/avatars/
  python tools/preview.py

Same as: python -m autopilot.main daily --count 1 --no-upload   -> out/<date>-1/short.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from autopilot import main  # noqa: E402

if __name__ == "__main__":
    main.main(["daily", "--count", "1", "--no-upload"])
