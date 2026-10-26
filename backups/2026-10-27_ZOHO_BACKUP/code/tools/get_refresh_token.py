"""ONE-TIME, on your own computer: get the YouTube refresh token for the channel.

1. pip install google-auth-oauthlib
2. Put the OAuth client file you downloaded from Google Cloud next to this script as client_secret.json
3. python tools/get_refresh_token.py
4. A browser opens -> log in with the Google account that OWNS the channel -> pick the channel -> Allow
   ("Google hasn't verified this app" -> Advanced -> Go to <app name>. It is your own app, that is fine.)
5. Copy the 3 values it prints into GitHub -> Settings -> Secrets and variables -> Actions
"""
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl"]

secret = Path(__file__).with_name("client_secret.json")
if not secret.exists():
    secret = Path("client_secret.json")
flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
info = json.loads(secret.read_text())
info = info.get("installed") or info.get("web")
print("\nAdd these as GitHub secrets:\n")
print("YT_CLIENT_ID      =", info["client_id"])
print("YT_CLIENT_SECRET  =", info["client_secret"])
print("YT_REFRESH_TOKEN  =", creds.refresh_token)
