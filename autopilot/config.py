"""Loads channel.yaml (what the channel is) + environment / GitHub secrets (keys)."""
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
ASSETS_DIR = ROOT / "assets"
OUT_DIR = ROOT / "out"

CH = yaml.safe_load((ROOT / os.getenv("CHANNEL_FILE", "channel.yaml")).read_text(encoding="utf-8"))

CHANNEL_NAME = CH["channel"]["name"]
CHANNEL_HANDLE = CH["channel"]["handle"]
LANGUAGE = CH["channel"].get("language", "Hinglish")
HASHTAGS = CH["channel"].get("hashtags", ["Shorts"])
DISCLAIMER = CH["channel"].get("disclaimer", "")

NICHE = CH["niche"]
CTA = NICHE.get("cta", "Follow karo {name}").format(name=CHANNEL_NAME)

FEEDS = CH["sources"].get("feeds", [])
KEYWORDS = CH["sources"].get("keywords", [])
LOOKBACK_DAYS = int(CH["sources"].get("lookback_days", 10))
EVERGREEN_FALLBACK = bool(CH["sources"].get("evergreen_fallback", True))

_S = CH.get("scripts", {})
SCRIPTS_PER_DAY = int(os.getenv("SCRIPTS_PER_DAY") or _S.get("per_day", 2))
SCRIPT_WORDS = (int(_S.get("words_min", 110)), int(_S.get("words_max", 150)))

_SCH = CH.get("schedule", {})
WINDOWS = _SCH.get("windows", {"morning": "07:00-08:00", "evening": "20:00-21:00"})
MIN_GAP_FROM_YESTERDAY = int(_SCH.get("min_gap_from_yesterday_minutes", 8))
MIN_LEAD_MINUTES = int(_SCH.get("min_lead_minutes", 30))

_C = CH.get("captions", {})
WHISPER_MODEL = os.getenv("WHISPER_MODEL") or _C.get("whisper_model", "small")
WHISPER_LANGUAGE = _C.get("whisper_language", "hi") or None
ROMAN_CAPTIONS = bool(_C.get("roman_captions", True))
CAPTION_MAX_WORDS = int(_C.get("max_words", 3))

MAX_VIDEO_SECONDS = float(CH.get("video", {}).get("max_seconds", 60))
BADGE = CH.get("labels", {}).get("hook_badge", "")


# Keys (GitHub -> Settings -> Secrets and variables -> Actions)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "")
YT_CATEGORY_ID = str(CH["youtube"].get("category_id", "28"))
YT_LANGUAGE = CH["youtube"].get("language", "hi")
