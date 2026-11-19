"""Strict check of a long-video script BEFORE it is rendered (the daily robot runs this; a failure = no render).

  python -m longform.validate docs/longform/scripts/<id>.json
Exit 1 with the list of problems. Checks: required fields, real sources, chapter cards, scene kinds that exist in the
renderer, beats vs voice lines, Zoho screens + click targets that exist in assets/screens/index.yaml, length, disclosure.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"HOOK", "CHAPTER", "CARTOON", "BOARD", "PODCAST", "OUTRO"}
UAE_ONLY = {"hook", "old_way", "five_corner", "fourteen_days", "penalty", "celebrate", "badge", "formula", "record", "timeline", "flow"}
WPM = 194  # Kokoro am_onyx at speed 1.1


def kinds():
    src = (ROOT / "longform/scenes/scenes.js").read_text() + (ROOT / "longform/scenes/generic.js").read_text()
    k = set(re.findall(r"(\w+): s[A-Z]\w*", src))
    return k


def check(path):
    sc = json.loads(Path(path).read_text())
    idx = yaml.safe_load((ROOT / "assets/screens/index.yaml").read_text())["screens"]
    K, bad = kinds(), []
    short = sc.get("format") == "short"
    need_f = (("id", "title", "voice", "description", "scenes", "tags", "sources", "headline", "source_line") if short else
              ("id", "title", "voice", "chapters", "description", "scenes", "thumb", "tags", "sources", "intro_chapter"))
    for f in need_f:
        if not sc.get(f):
            bad.append(f"missing '{f}'")
    if len(sc.get("title", "")) > 100:
        bad.append("title > 100 chars")
    src = [s for s in sc.get("sources", []) if str(s.get("url", "")).startswith("http")]
    if len(src) < 2:
        bad.append("need at least 2 sources with a url")
    d = sc.get("description", "")
    for need in (("AI-generated",) if short else ("{chapters}", "AI-generated", "Not affiliated")):
        if need not in d:
            bad.append(f"description must contain '{need}'")
    if "zoho" in (sc.get("title", "") + d).lower() and "Not affiliated" not in d:
        bad.append("mentions Zoho -> description must contain 'Not affiliated ...' line")
    if not short:
        allowed = set(re.findall(r"^\| `([a-z-]+)` \|", (ROOT / "docs/longform/STRUCTURES.md").read_text(), re.M))
        st = sc.get("structure")
        if st not in allowed:
            bad.append(f"'structure' must be one of {sorted(allowed)} (script-writer agent, docs/longform/STRUCTURES.md)")
        else:
            used = ROOT / "docs/longform/structures-used.md"
            rows = [r.split("|") for r in used.read_text().splitlines() if r.count("|") >= 4] if used.exists() else []
            last = [r[3].strip() for r in rows if r[1].strip() == "long" and r[2].strip() != sc.get("id")][-4:]
            if st in last:
                bad.append(f"structure '{st}' was used in the last 4 long videos ({last}) - pick another one")
    th = sc.get("thumb") or {}
    if not short and (not th.get("l1") or not th.get("l2")):
        bad.append("thumb needs l1 + l2")
    if short and any(s.get("type") in ("CHAPTER", "OUTRO") for s in sc.get("scenes", [])):
        bad.append("a Short has no CHAPTER / OUTRO scenes")
    chap = [s for s in sc.get("scenes", []) if s.get("type") == "CHAPTER"]
    if not short and len(chap) != len(sc.get("chapters", [])):
        bad.append(f"{len(chap)} CHAPTER scenes but {len(sc.get('chapters', []))} chapter names")
    for i, s in enumerate(chap):
        if (s.get("visual") or {}).get("num") != i + 1:
            bad.append(f"{s.get('id')}: chapter num should be {i + 1}")
    words, ids = 0, set()
    for s in sc.get("scenes", []):
        sid, ty, v, L = s.get("id"), s.get("type"), s.get("visual") or {}, s.get("lines") or []
        if sid in ids:
            bad.append(f"duplicate scene id {sid}")
        ids.add(sid)
        if ty not in TYPES:
            bad.append(f"{sid}: unknown type {ty}")
            continue
        if not L:
            bad.append(f"{sid}: no lines")
        for ln in L:
            words += len(ln.split())
            if len(ln) > 260:
                bad.append(f"{sid}: line too long ({len(ln)} chars) - split it")
            if re.search(r"[<>]", ln):
                bad.append(f"{sid}: '<' or '>' in a line")
        if ty in ("CHAPTER", "PODCAST"):
            pass
        else:
            k = v.get("kind")
            if k not in K:
                bad.append(f"{sid}: kind '{k}' does not exist (have: {sorted(K)})")
            elif k in UAE_ONLY and not sc.get("id", "").startswith("uae-"):
                bad.append(f"{sid}: kind '{k}' is drawn only for the UAE e-invoicing video - use a generic kind")
            n = len(L)
            if k in ("hook2", "story") and len(v.get("beats", [])) != n:
                bad.append(f"{sid}: {len(v.get('beats', []))} beats for {n} lines (must be equal)")
            if k == "checklist" and len(v.get("items", [])) != n:
                bad.append(f"{sid}: checklist needs one item per line ({n})")
            if k == "checklist" and n > 6:
                bad.append(f"{sid}: checklist max 6 items")
            if k in ("stat", "headline") and not 1 <= len(v.get("stats" if k == "stat" else "items", [])) <= 3:
                bad.append(f"{sid}: {k} needs 1-3 entries")
            if k == "dates" and not 1 <= len(v.get("items", [])) <= 6:
                bad.append(f"{sid}: dates needs 1-6 items")
            if k == "flow2" and not 2 <= len(v.get("steps", [])) <= 5:
                bad.append(f"{sid}: flow2 needs 2-5 steps")
            if k == "compare":
                for side in ("left", "right"):
                    if not (v.get(side) or {}).get("items"):
                        bad.append(f"{sid}: compare needs {side}.items")
                if not v.get("cues"):
                    bad.append(f"{sid}: compare needs cues [[line, 'L0', 'R0'], ...]")
                for c in v.get("cues", []):
                    if c[0] >= n:
                        bad.append(f"{sid}: compare cue line {c[0]} >= {n} lines")
            if k == "outro" and not v.get("next"):
                bad.append(f"{sid}: outro needs 'next'")
        if ty == "PODCAST":
            if not v.get("path") or not v.get("actions"):
                bad.append(f"{sid}: PODCAST needs path + actions")
            last = None
            for a in v.get("actions", []):
                if a.get("cue", 0) >= len(L):
                    bad.append(f"{sid}: action cue {a.get('cue')} >= {len(L)} lines")
                if a.get("screen"):
                    if a["screen"] not in idx:
                        bad.append(f"{sid}: screen '{a['screen']}' not in assets/screens/index.yaml")
                        continue
                    last = a["screen"]
                if a.get("target"):
                    if not last:
                        bad.append(f"{sid}: target before any screen")
                    elif a["target"] not in (idx[last].get("targets") or {}):
                        bad.append(f"{sid}: target '{a['target']}' not on {last}")
            if v.get("actions") and not v["actions"][0].get("screen"):
                bad.append(f"{sid}: first PODCAST action must set a screen")
    mins = words / WPM
    if short:
        if not 25 <= mins * 60 <= 52:
            bad.append(f"spoken length ~{mins * 60:.0f} s (a Short wants 25-52 s)")
    elif not 6.6 <= mins <= 11.0:
        bad.append(f"spoken length ~{mins:.1f} min (want 6.6-11 so the video is 7-12 min, QA rule)")
    return bad, mins


if __name__ == "__main__":
    bad, mins = check(sys.argv[1])
    if bad:
        print("SCRIPT PROBLEMS:\n- " + "\n- ".join(bad))
        sys.exit(1)
    print(f"[validate] OK (~{mins:.1f} min spoken)")
