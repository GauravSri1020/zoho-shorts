"""Tiny JSON state kept in the repo (committed back by the workflow)."""
import json
from .config import STATE_DIR

STATE_FILE = STATE_DIR / "state.json"
DEFAULT = {
    "next_id": 1,
    "covered_links": [],      # source stories already used
    "problems": [],           # problems already scripted (so they never repeat)
    "scripts": {},            # "Z0007" -> {problem, title, hook_text, ..., status: pending|published}
    "slots": [],              # [{"date": "2026-10-11", "window": "evening", "minute": 1234, "video_id": ...}]
    "failures": {},           # drive folder/file id -> failed attempts
    "seen_comments": [],      # comment ids already sent to you in the digest
}


def load():
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    for k, v in DEFAULT.items():
        data.setdefault(k, json.loads(json.dumps(v)))
    return data


def save(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data["covered_links"] = data["covered_links"][-600:]
    data["problems"] = data["problems"][-300:]
    data["slots"] = data["slots"][-200:]
    data["seen_comments"] = data["seen_comments"][-3000:]
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
