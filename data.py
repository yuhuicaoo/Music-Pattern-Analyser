import streamlit as st
from datetime import datetime
from config import supabase


def fetch_top_tracks(sp):
    return sp.current_user_top_tracks(limit=50, time_range="short_term")["items"]


def cache_track_images(tracks):
    if "track_imgs" not in st.session_state:
        st.session_state.track_imgs = {
            track["id"]: track["album"]["images"][0]["url"] for track in tracks
        }


def store_tracks(user_id, tracks):
    month_year = datetime.now().strftime("%m-%Y")
    rows = [
        {
            "user_id": user_id,
            "track_id": track["id"],
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "rank": idx + 1,
            "month": month_year,
        }
        for idx, track in enumerate(tracks)
    ]
    supabase.table("user_tracks").upsert(
        rows, on_conflict="user_id,track_id,month"
    ).execute()

def already_fetched_this_month(user_id):
    month_year = datetime.now().strftime("%m-%Y")
    result = (
        supabase.table("user_tracks")
        .select("track_id")
        .eq("user_id", user_id)
        .eq("month", month_year)
        .limit(1)
        .execute()
    )
    return len(result.data) > 0


def fetch_data_and_store(sp, user_id):
    with st.spinner("Fetching your top tracks from Spotify..."):
        tracks = fetch_top_tracks(sp)
        cache_track_images(tracks)
        store_tracks(user_id, tracks)


def load_user_tracks(user_id):
    month_year = datetime.now().strftime("%m-%Y")
    return (
        supabase.table("user_tracks")
        .select("*")
        .eq("user_id", user_id)
        .eq("month", month_year)
        .order("rank")
        .execute().data
    )

def delete_user_data(user_id):
    supabase.table("user_tracks").delete().eq("user_id", user_id).execute()
    supabase.table("user_profiles").delete().eq("user_id",user_id).execute()
