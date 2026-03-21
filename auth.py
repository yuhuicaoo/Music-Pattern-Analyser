import spotipy
import streamlit as st
from config import BACKEND_URL, supabase

def get_spotify_client():
    return spotipy.Spotify(auth=st.query_params["token"])

def save_user_session(sp):
    user = sp.me()
    user_id = user['id']
    display_name = user['display_name']

    # insert user data into database
    supabase.table("user_profiles").upsert({
        "user_id": user_id,
        "display_name": display_name,
        "access_token": st.query_params["token"],
    }, on_conflict="user_id").execute()

    st.session_state.user_id = user_id
    st.session_state.display_name = display_name

def get_returning_user():
    if "user_id" in st.session_state:
        return st.session_state.user_id, st.session_state.display_name
    return None, None

def show_login():
    st.markdown(f'''
        <a href="{BACKEND_URL}/login" target="_self" style="
            display: inline-block;
            background-color: #1DB954;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
        ">Login with Spotify</a>
    ''', unsafe_allow_html=True)

def show_consent():
    st.warning("Do you agree to giving access to your Spotify listening data and storing it in our database?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, I consent", use_container_width=True):
            st.session_state.consent_given = True
            st.rerun()
    with col2:
        if st.button("No, I do not give consent", use_container_width=True):
            st.info("Your data will not be accessed or stored")
            st.stop()