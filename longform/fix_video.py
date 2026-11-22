"""Update an already-uploaded video: title / description / tags (keywords) and the custom thumbnail.

  python -m longform.fix_video <request.json>

request: {"video_id": "...", "title": "...", "description_prepend": "...", "tags": [...], "thumb": "previews/<id>-thumb.jpg",
          "publish_at": "2026-11-23T08:00:00Z"}   (publish_at only: move a still-private scheduled video to a new time)
Keeps everything else (category, language, publish status). Needs youtube.force-ssl (already in the token).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main(req_path):
    from autopilot import google_apis as g
    r = json.loads(Path(req_path).read_text())
    yt = g.youtube()
    vid = r["video_id"]
    cur = yt.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
    sn = {"title": r.get("title") or cur["title"], "categoryId": cur["categoryId"],
          "description": cur.get("description", ""), "tags": r.get("tags") or cur.get("tags", [])}
    for k in ("defaultLanguage", "defaultAudioLanguage"):
        if cur.get(k):
            sn[k] = cur[k]
    if r.get("description_prepend") and not sn["description"].startswith(r["description_prepend"][:40]):
        sn["description"] = r["description_prepend"].rstrip() + "\n\n" + sn["description"]
    if r.get("privacy") in ("private", "unlisted"):  # 23 Nov 2026: take a scheduled / public video off (reversible)
        st = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]
        st = {k: st[k] for k in ("selfDeclaredMadeForKids", "embeddable", "license", "publicStatsViewable",
                                 "containsSyntheticMedia") if k in st}
        st["privacyStatus"] = r["privacy"]
        yt.videos().update(part="status", body={"id": vid, "status": st}).execute()
        print(f"[fix] {vid}: now {r['privacy']} (publish time removed)")
        return
    if r.get("publish_at"):
        st = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]
        if st.get("privacyStatus") != "private":
            print(f"[fix] {vid}: already {st.get('privacyStatus')} - publish time not changed")
        else:
            st = {k: st[k] for k in ("privacyStatus", "selfDeclaredMadeForKids", "embeddable", "license",
                                     "publicStatsViewable", "containsSyntheticMedia") if k in st}
            st["publishAt"] = r["publish_at"]
            yt.videos().update(part="status", body={"id": vid, "status": st}).execute()
            print(f"[fix] {vid}: now public at {r['publish_at']}")
        if not (r.get("title") or r.get("tags") or r.get("description_prepend") or r.get("thumb")):
            return
    yt.videos().update(part="snippet", body={"id": vid, "snippet": sn}).execute()
    print(f"[fix] {vid}: title / description / {len(sn['tags'])} tags updated")
    if r.get("thumb"):
        out = Path("thumb.jpg")
        subprocess.run(["git", "fetch", "--depth=1", "origin", "longform-previews"], check=True)
        out.write_bytes(subprocess.check_output(["git", "show", f"FETCH_HEAD:{r['thumb']}"]))
        from googleapiclient.http import MediaFileUpload
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(out), mimetype="image/jpeg")).execute()
        print(f"[fix] {vid}: thumbnail set")


if __name__ == "__main__":
    main(sys.argv[1])
