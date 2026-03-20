import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

CLIENT_ID = st.secrets["spotify"]["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["spotify"]["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = st.secrets["spotify"]["SPOTIFY_REDIRECT_URI"]
SCOPE = "user-top-read"

# Streamlit UI
st.title("Spotify Top Tracks Collector")

# Step 1: Generate Spotify login URL
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

# Check if we have a cached token
token_info = sp_oauth.get_cached_token()

if not token_info:
    # No cached token, show login button
    auth_url = sp_oauth.get_authorize_url()
    st.markdown(f"[Login with Spotify]({auth_url})")
else:
    # Token exists, fetch top tracks automatically
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user = sp.me()
    username = user["display_name"]
    st.success(f"Hello {username}!")

    results = sp.current_user_top_tracks(limit=50)
    tracks = [{
        "track_id": t['id'],
        "artist": t['artists'][0]['name'],
        "track_name": t['name']
    } for t in results['items']]

    df = pd.DataFrame(tracks)
    st.dataframe(df)

    # CSV download
    csv_file = f"{username}_top50_tracks.csv"
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name=csv_file,
        mime="text/csv"
    )