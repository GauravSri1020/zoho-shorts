"""Loads channel.yaml (what the channel is) + environment / GitHub secrets (keys)."""
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
ASSETS_DIR = ROOT / "assets"
OUT_DIR = ROOT / "out"

def _load(rel):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8")) or {}


def _merge(base, over):
    """Niche file on top of the niche it extends, ONE level deep: a section the niche writes (channel, niche,
    benchmark, ...) takes the base section and replaces only the keys the niche gives - so pillars, feeds,
    solution types, references are the niche's own (never mixed with Zoho's), while the presenter / looks /
    gestures / schedule / QA limits it does not mention come from the base."""
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = {**out[k], **v} if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


# 27 Oct 2026 - NICHE SWITCH. channel.yaml = only the switch ("active_niche") + the list of niche files.
# Every niche is its own file in niches/ (niches/zoho.yaml = the old channel.yaml, not one line changed).
# One run can override it: env NICHE (GitHub: Run workflow -> niche). An old-style channel.yaml (no
# active_niche) still works exactly as before = the Zoho niche.
_SWITCH = _load(os.getenv("CHANNEL_FILE", "channel.yaml"))
if "active_niche" in _SWITCH:
    NICHES = dict(_SWITCH.get("niches") or {})
    NICHE_ID = (os.getenv("NICHE") or "").strip() or str(_SWITCH["active_niche"]).strip()
    if NICHE_ID not in NICHES:
        raise SystemExit(f"niche '{NICHE_ID}' is not listed in channel.yaml -> niches ({', '.join(NICHES)})")
    CH = _load(NICHES[NICHE_ID])
    if CH.get("extends"):
        CH = _merge(_load(NICHES[CH["extends"]]), {k: v for k, v in CH.items() if k != "extends"})
else:
    NICHES = {"zoho": os.getenv("CHANNEL_FILE", "channel.yaml")}
    NICHE_ID = "zoho"
    CH = _SWITCH
IS_ZOHO = NICHE_ID == "zoho"

CHANNEL_NAME = CH["channel"]["name"]
CHANNEL_HANDLE = CH["channel"]["handle"]
LANGUAGE = CH["channel"].get("language", "Hinglish")
HASHTAGS = CH["channel"].get("hashtags", ["Shorts"])
DISCLAIMER = CH["channel"].get("disclaimer", "")

NICHE = CH["niche"]
CTA = NICHE.get("cta", "Follow karo {name}").format(name=CHANNEL_NAME)
PILLARS = NICHE.get("pillars", {}) or {}
PROBLEM_BANK = ROOT / CH.get("problem_bank", "research/problem_bank.yaml")
LOCALES = [str(x) for x in ((CH.get("localize") or {}).get("languages") or [])]

FEEDS = CH["sources"].get("feeds", [])
KEYWORDS = CH["sources"].get("keywords", [])
LOOKBACK_DAYS = int(CH["sources"].get("lookback_days", 10))
EVERGREEN_FALLBACK = bool(CH["sources"].get("evergreen_fallback", True))
# 10 Nov 2026 (Gaurav): every Short must be built on TRENDING NEWS. feeds = news, community_feeds = what people ask
# (used only as proof that the pain is real, never as the topic). No problem bank / evergreen topics then.
COMMUNITY_FEEDS = CH["sources"].get("community_feeds", [])
TRENDING_ONLY = bool(CH["sources"].get("trending_only", False))
NEWS_MAX_AGE_HOURS = int(CH["sources"].get("news_max_age_hours", LOOKBACK_DAYS * 24))
NEWS_MUST_MENTION = [str(k).lower() for k in (CH["sources"].get("news_must_mention") or [])]  # e.g. ["zoho"]

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
