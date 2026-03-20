import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
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

auth_url = sp_oauth.get_authorize_url()
st.markdown(f"[Login with Spotify]({auth_url})")

# Step 2: User pastes redirect URL here
redirect_response = st.text_input("After login, paste the full URL Spotify redirected you to:")

if redirect_response:
    token_info = sp_oauth.get_access_token(redirect_response)
    if token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user = sp.me()
        username = user["display_name"]
        st.success(f"Hello {username}!")

        # Step 3: Fetch top tracks
        results = sp.current_user_top_tracks(limit=50)
        tracks = []
        for item in results['items']:
            tracks.append({
                "track_id": item['id'],
                "artist": item['artists'][0]['name'],
                "track_name": item['name'],
            })

        df = pd.DataFrame(tracks)
        st.dataframe(df)

        # Save CSV
        csv_file = f"{username}_top50_tracks.csv"
        df.to_csv(csv_file, index=False)
        st.success(f"Saved CSV: {csv_file}")

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=csv_file,
            mime="text/csv"
        )