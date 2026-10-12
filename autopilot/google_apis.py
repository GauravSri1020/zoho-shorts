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


def my_channel_id(yt):
    return yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]


def reply(yt, parent_id, text):
    yt.comments().insert(part="snippet", body={"snippet": {"parentId": parent_id, "textOriginal": text}}).execute()


def recent_comment_threads(yt, channel_id, max_results=50):
    r = yt.commentThreads().list(part="snippet,replies", allThreadsRelatedToChannelId=channel_id,
                                 maxResults=max_results, order="time", textFormat="plainText").execute()
    return r.get("items", [])
