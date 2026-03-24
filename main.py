import os
import secrets
from datetime import datetime

import spotipy
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth
from supabase import create_client

app = FastAPI()

FRONTEND_URL = "https://music-pattern-analyser.streamlit.app"


# Initialize Supabase with environment variables
supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)



# Initialize Spotify OAuth with environment variables
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-top-read user-read-private user-read-email",
    cache_handler=spotipy.cache_handler.MemoryCacheHandler(),
    show_dialog=True
)

@app.get("/login")
def login():
    return RedirectResponse(url=sp_oauth.get_authorize_url())


@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing Spotify code"}

    token_info = sp_oauth.get_access_token(code, check_cache=False)

    sp = spotipy.Spotify(auth=token_info["access_token"])
    user = sp.current_user()

    user_id = user["id"]
    display_name = user.get("display_name")
    profile_img = user["images"][0]["url"] if user.get("images") else None
    expires_at = datetime.fromtimestamp(token_info["expires_at"]).isoformat()

    # 1) ensure parent row exists first
    supabase.table("user_profiles").upsert(
        {
            "user_id": user_id,
            "display_name": display_name,
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"],
            "token_expiry": expires_at,
            "profile_img": profile_img,
        },
        on_conflict="user_id",
    ).execute()

    # 2) now insert child row
    key = secrets.token_urlsafe(32)
    supabase.table("spotify_sessions").insert({
        "key": key,
        "user_id": user_id,
        "token": token_info
    }).execute()

    return RedirectResponse(url=f"{FRONTEND_URL}/?session={key}")

@app.get("/token/{key}")
def get_token(key):
    result = (
        supabase.table("spotify_sessions")
        .select("token, user_id")
        .eq("key", key)
        .single()
        .execute()
    )

    if not result.data:
        return {"error": "Invalid or expired session"}

    data = result.data

    supabase.table("spotify_sessions").delete().eq("key",key).execute()

    return {
        "token_info": data["token"],
        "user_id": data["user_id"]
    }
