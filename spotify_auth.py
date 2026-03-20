import spotipy
import streamlit as st
from config import BACKEND_URL

def get_spotify_client():
    return spotipy.Spotify(auth=st.query_params["token"])

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