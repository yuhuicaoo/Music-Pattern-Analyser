import streamlit as st
from config import supabase

def fetch_top_tracks(sp):
    return sp.current_user_top_tracks(limit=50, time_range="short_term")["items"]

def cache_track_images(tracks):
    if "track_imgs" not in st.session_state:
        st.session_state.track_imgs = {
            track["id"]: track["album"]["images"][0]["url"]
            for track in tracks
        }

def store_tracks(username, tracks):
    rows = [
        {
            "username": username,
            "track_id": track["id"],
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
        }
        for track in tracks
    ]
    supabase.table("user_tracks").insert(rows).execute()

def fetch_data_and_store(sp, username):
    with st.spinner("Fetching your top tracks from Spotify..."):
        tracks = fetch_top_tracks(sp)
        cache_track_images(tracks)
        store_tracks(username, tracks)

def load_user_tracks(username):
    return supabase.table("user_tracks").select("*").eq("username", username).execute().data