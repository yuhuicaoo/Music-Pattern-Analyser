import spotipy
import pandas as pd
import streamlit as st
from supabase import create_client

SUPABASE_URL= st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

supabase = create_client(supabase_url=SUPABASE_URL,supabase_key=SUPABASE_KEY)

backend_url = "https://music-pattern-analyser.onrender.com"

def show_login():
    st.markdown(f'''
        <a href="{backend_url}/login" target="_self" style="
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

def fetch_data_and_store(sp, username):
    with st.spinner("Fetching your top tracks from Spotify..."):
        results = sp.current_user_top_tracks(limit=50, time_range="short_term")

        # keep album images to display.
        if "track_imgs" not in st.session_state:
            st.session_state.track_imgs = {
                track["id"]: track["album"]["images"][0]['url'] for track in results["items"]
            }

        for track in results["items"]:
            supabase.table("user_tracks").insert({
                "username": username,
                "track_id": track['id'],
                "track_name": track['name'],
                "artist": track['artists'][0]['name'],
            }).execute()

def show_tracks(username):
    with st.spinner("Loading your top 50 songs..."):
        data = supabase.table("user_tracks").select("*").eq("username", username).execute()


    st.subheader("Your Top 50 Tracks This Month")

    with st.container(height=500):
        for idx, row in enumerate(data.data):
            col1, col2, col3 = st.columns([1, 2, 10])

            with col1:
                st.write(idx + 1)

            with col2:
                image_url = st.session_state.track_imgs.get(row["track_id"])
                if image_url:
                    st.image(image_url, width=50)

            with col3:
                st.markdown(f"**{row['track_name']}**")
                st.caption(row['artist'])

def main():
    st.title("Spotify Top Tracks Collector")

    if "token" not in st.query_params:
        show_login()
        return

    st.session_state.setdefault("consent_given", False)
    st.session_state.setdefault("data_fetched", False)

    # consent to collect data
    if not st.session_state.consent_given:
        show_consent()
        return

    sp = spotipy.Spotify(auth=st.query_params["token"])
    user = sp.me()
    username = user["display_name"]
    st.success(f"Hello {username}!")

    # only fetch data if it hasnt already been fetched
    if not st.session_state.data_fetched:
        fetch_data_and_store(sp, username)
        st.session_state.data_fetched = True

    show_tracks(username)


main()