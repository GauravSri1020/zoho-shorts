"""Read-only channel audit (23 Nov 2026): every upload with privacy, publish time, length, views - printed as JSON.
Run by .github/workflows/channel-audit.yml (manual). Changes nothing on YouTube."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from autopilot import google_apis as g


def main(n=120):
    yt = g.youtube()
    ch = yt.channels().list(part="contentDetails,statistics,snippet", mine=True).execute()["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while len(ids) < n:
        r = yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        tok = r.get("nextPageToken")
        if not tok:
            break
    rows = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,status,contentDetails,statistics", id=",".join(ids[k:k + 50])).execute()
        for v in r.get("items", []):
            d = v["contentDetails"].get("duration", "")
            m = re.match(r"PT(?:(\d+)M)?(?:(\d+)S)?", d) or None
            secs = (int(m.group(1) or 0) * 60 + int(m.group(2) or 0)) if m else None
            rows.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"].get("publishedAt"),
                         "privacy": v["status"].get("privacyStatus"), "publish_at": v["status"].get("publishAt"),
                         "secs": secs, "views": int(v["statistics"].get("viewCount", 0)),
                         "likes": int(v["statistics"].get("likeCount", 0)),
                         "comments": int(v["statistics"].get("commentCount", 0))})
    print("AUDIT_JSON_START")
    print(json.dumps({"channel": ch["snippet"]["title"], "stats": ch["statistics"], "videos": rows}))
    print("AUDIT_JSON_END")


if __name__ == "__main__":
    main()
