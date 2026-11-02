"""YouTube login (refresh token).

Scopes:
  youtube.upload     - upload the Shorts (scheduled, private until publish time)
  youtube.force-ssl  - read and reply to comments
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CATEGORY_ID, YT_LANGUAGE

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl"]


def _creds():
    if not (YT_CLIENT_ID and YT_CLIENT_SECRET and YT_REFRESH_TOKEN):
        raise SystemExit("Google secrets missing (YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN)")
    return Credentials(None, refresh_token=YT_REFRESH_TOKEN, client_id=YT_CLIENT_ID,
                       client_secret=YT_CLIENT_SECRET, token_uri="https://oauth2.googleapis.com/token",
                       scopes=SCOPES)


# ------------------------------------------------------------------ YouTube
def youtube():
    return build("youtube", "v3", credentials=_creds(), cache_discovery=False)


def upload(yt, video_path, title, description, tags, publish_at, localizations=None):
    """Uploads as private with publishAt -> YouTube makes it public at that exact time.
    localizations: {"ar": {"title", "description"}, ...} -> viewers see the title in their own language."""
    body = {
        "snippet": {"title": title[:100], "description": description[:4900],
                    "tags": [t for t in tags if t][:15], "categoryId": YT_CATEGORY_ID,
                    "defaultLanguage": YT_LANGUAGE, "defaultAudioLanguage": YT_LANGUAGE},
        # AI avatar + AI voice = realistic synthetic media -> YouTube's "altered or synthetic content" label ON.
        "status": {"privacyStatus": "private", "publishAt": publish_at,
                   "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True},
    }
    parts = "snippet,status"
    loc = {k: v for k, v in (localizations or {}).items() if k != YT_LANGUAGE and v.get("title")}
    if loc:
        body["localizations"] = loc
        parts += ",localizations"

    def _insert(b, p):
        return yt.videos().insert(part=p, body=b,
                                  media_body=MediaFileUpload(str(video_path), chunksize=8 * 1024 * 1024,
                                                             resumable=True, mimetype="video/mp4"))
    req = _insert(body, parts)
    resp = None
    try:
        while resp is None:
            status, resp = req.next_chunk()
            if status:
                print(f"[yt] upload {int(status.progress() * 100)}%")
    except Exception as e:
        if not loc or resp is not None:
            raise
        # a bad translation must never block the upload: retry without localizations
        print(f"[yt] upload with localizations failed ({str(e)[:160]}) - retrying without them")
        body.pop("localizations", None)
        req, resp = _insert(body, "snippet,status"), None
        while resp is None:
            status, resp = req.next_chunk()
    print(f"[yt] uploaded https://youtube.com/shorts/{resp['id']} (public at {publish_at})"
          + (f", titles in {', '.join(loc)}" if "localizations" in body else ""))
    return resp["id"]


def set_thumbnail(yt, video_id, jpg):
    """Custom thumbnail (cover.jpg). Best effort: YouTube may refuse it (channel not phone-verified, or Shorts
    feed ignoring it) - the Short already OPENS on the same cover, so a refusal is only logged, never fatal."""
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(jpg), mimetype="image/jpeg")).execute()
        print(f"[yt] thumbnail set for {video_id}")
        return True
    except Exception as e:
        print(f"[yt] thumbnail not set ({str(e)[:200]}) - the Short still opens on its cover frame")
        return False


def scheduled_times(yt, days_back=3):
    """[(video_id, aware datetime)] of every upload that is scheduled (private + publishAt) or went public in the
    last days_back days. The scheduler counts these so a day never gets more than schedule.per_day videos - also
    when a video was uploaded by hand or by a parallel run."""
    import datetime as dt
    ch = yt.channels().list(part="contentDetails", mine=True).execute()
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    for _ in range(4):  # newest 200 uploads is plenty
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50,
                                    pageToken=token).execute()
        ids += [it["contentDetails"]["videoId"] for it in r.get("items", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days_back)
    out = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="status,snippet", id=",".join(ids[k:k + 50])).execute()
        for v in r.get("items", []):
            st = v.get("status", {}) or {}
            if st.get("privacyStatus") == "private" and st.get("publishAt"):
                t = st["publishAt"]
            elif st.get("privacyStatus") == "public":
                t = (v.get("snippet") or {}).get("publishedAt")
            else:
                continue
            if not t:
                continue
            when = dt.datetime.fromisoformat(t.replace("Z", "+00:00"))
            if when >= since:
                out.append((v["id"], when))
    return out


def my_channel_id(yt):
    return yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]


def reply(yt, parent_id, text):
    yt.comments().insert(part="snippet", body={"snippet": {"parentId": parent_id, "textOriginal": text}}).execute()


def recent_comment_threads(yt, channel_id, max_results=50):
    r = yt.commentThreads().list(part="snippet,replies", allThreadsRelatedToChannelId=channel_id,
                                 maxResults=max_results, order="time", textFormat="plainText").execute()
    return r.get("items", [])
