import streamlit as st
from supabase import create_client
from streamlit_cookies_controller import CookieController
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler


BACKEND_URL = "https://music-pattern-analyser.onrender.com"

SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

supabase = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
cookie = CookieController()

sp_oauth = SpotifyOAuth(
    client_id=st.secrets["spotify"]["SPOTIFY_CLIENT_ID"],
    client_secret=st.secrets["spotify"]["SPOTIFY_CLIENT_SECRET"],
    redirect_uri=st.secrets["spotify"]["SPOTIFY_REDIRECT_URI"],
    scope="user-top-read user-read-private user-read-email",
    cache_handler=MemoryCacheHandler(),
    show_dialog=True
)
