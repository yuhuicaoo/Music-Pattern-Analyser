import os
from fastapi import FastAPI, Request
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import RedirectResponse
import secrets
from config import supabase, sp_oauth
import requests as req

app = FastAPI()

@app.get("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

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
