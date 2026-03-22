import streamlit as st
from supabase import create_client
from streamlit_cookies_controller import CookieController


BACKEND_URL = "https://music-pattern-analyser.onrender.com"

SCOPE = "user-top-read user-read-private user-read-email"
SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

supabase = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
cookie = CookieController()
