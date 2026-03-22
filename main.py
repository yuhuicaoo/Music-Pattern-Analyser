import os
from fastapi import FastAPI, Request
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import RedirectResponse
import secrets
from supabase import create_client

app = FastAPI()

# Initialize Spotify OAuth with environment variables
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-top-read user-read-private user-read-email",
    cache_path=None,
    show_dialog=True
)

# Initialize Supabase with environment variables
supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)

@app.get("/login")
def login():
    return RedirectResponse(url=sp_oauth.get_authorize_url())

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")

    token_info = sp_oauth.get_access_token(code)
    key = secrets.token_urlsafe(32)

    supabase.table("spotify_sessions").insert({
        "key": key,
        "token": token_info
    }).execute()

    return RedirectResponse(
        url=f"https://music-pattern-analyser.streamlit.app/?session={key}"
    )

@app.get("/token/{key}")
def get_token(key):
    result = (
        supabase.table("spotify_sessions")
        .select("token")
        .eq("key", key)
        .single()
        .execute()    
    )

    if not result.data:
        return {"error": "Invalid or expired session"}

    token = result.data["token"]

    supabase.table("spotify_sessions").delete().eq("key",key).execute()

    return token
