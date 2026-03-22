import streamlit as st
from streamlit_cookies_controller import CookieController
from spotipy.oauth2 import SpotifyOAuth


BACKEND_URL = "https://music-pattern-analyser.onrender.com"

cookie = CookieController()

sp_oauth = SpotifyOAuth(
    client_id=st.secrets["spotify"]["SPOTIFY_CLIENT_ID"],
    client_secret=st.secrets["spotify"]["SPOTIFY_CLIENT_SECRET"],
    redirect_uri=st.secrets["spotify"]["SPOTIFY_REDIRECT_URI"],
    scope="user-top-read user-read-private user-read-email",
    cache_path=None,
    show_dialog=True
)
