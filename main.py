import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "user-top-read"

st.title("Spotify Top Tracks Collector")

# authentication
st.write("Click below to log in with Spotify")
auth_url = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
).get_authorize_url()

st.markdown(f"[Login to Spotify]({auth_url})")

redirect_response = st.text_input("Paste the full redirect URL here:")
print(redirect_response)

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     redirect_uri=REDIRECT_URI,
#     scope=SCOPE
# ))

# results = sp.current_user_top_tracks(limit=50)

# # store track data.
# tracks, track_ids = [], []
# for item in results['items']:
#     track_ids.append(item['id'])
#     tracks.append({
#         "track_id": item['id'],
#         "artist": item['artists'][0]['name'],
#         "track_name": item['name'],
#     })

# # Write and save data to a csv
# df = pd.DataFrame(tracks)
# username = sp.me()['display_name']
# df.to_csv(f"{username}_top50_tracks.csv", index=False)
