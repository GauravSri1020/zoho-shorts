"""YouTube title / description (with chapters from the real render timings) / tags for a long video.

  python -m longform.meta docs/longform/scripts/<id>.json out/video/plan.json previews/<id>.meta.json
"""
import datetime as dt
import json
import sys
from pathlib import Path


def ts(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def build(script, plan, out):
    sc = json.loads(Path(script).read_text())
    scenes = json.loads(Path(plan).read_text())
    chap = [(0.0, sc["chapters"][0] if False else "Intro")]
    starts = [s["start"] for s in scenes if s["type"] == "CHAPTER"]
    chap = [(0.0, "UAE e-invoicing in 30 seconds")] + [(t, n) for t, n in zip(starts, sc["chapters"])]
    lines = "\n".join(f"{ts(t)} {n}" for t, n in chap)
    desc = sc["description"].replace("{chapters}", lines).replace("{date}", dt.date.today().strftime("%d %b %Y"))
    tags = sc.get("tags") or ["UAE e-invoicing", "Zoho Books", "Zoho Books UAE", "e-invoicing UAE 2027", "Peppol UAE",
                              "UAE VAT", "EmaraTax", "FTA UAE", "accredited service provider", "PINT AE",
                              "Zoho Books tutorial", "GSX Automation"]
    meta = {"title": sc["title"][:100], "description": desc, "tags": tags}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    return meta


if __name__ == "__main__":
    m = build(*sys.argv[1:4])
    print(m["title"])
    print(m["description"])
