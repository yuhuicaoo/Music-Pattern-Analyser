import os
from fastapi import FastAPI, Request
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import RedirectResponse
import secrets

app = FastAPI()

# Spotify keys
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "user-top-read user-read-private user-read-email"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=None,
)

token_store = {}

@app.get("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")

    token_info = sp_oauth.get_access_token(code)
    key = secrets.token_urlsafe(32)
    token_store[key]= token_info

    return RedirectResponse(
        url=f"https://music-pattern-analyser.streamlit.app/?session={key}"
    )

@app.get("/token/{key}")
def get_token(key):
    token = token_store.pop(key, None)
    if not token:
        return {"error": "Invalid or expired session"}
    return token