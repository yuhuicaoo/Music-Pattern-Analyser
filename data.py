import streamlit as st
from datetime import datetime
from config import supabase


def fetch_top_tracks(sp):
    return sp.current_user_top_tracks(limit=50, time_range="short_term")["items"]

def refresh_user_tracks(user_id, tracks):
    month_year = datetime.now().strftime("%m-%Y")
    rows = [
        {
            "user_id": user_id,
            "track_id": track["id"],
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "rank": idx + 1,
            "image_url": track["album"]["images"][0]["url"]
        }
        for idx, track in enumerate(tracks)
    ]

    supabase.table("user_tracks").delete().eq("user_id", user_id).execute()
    supabase.table("user_tracks").insert(rows).execute()

def needs_refresh(user_id):
    profile = (
        supabase.table("user_profiles")
        .select("last_fetched")
        .eq("user_id", user_id)
        .single()
        .execute().data
    )

    # data has not been fetched for this user
    if not profile["last_fetched"]:
        return True
    
    last_fetched = datetime.fromisoformat(profile["last_fetched"])
    return (datetime.now() - last_fetched).days >= 30

def update_last_fetched(user_id):
    supabase.table("user_profiles").update({
        "last_fetched": datetime.now().isoformat()
    }).eq("user_id", user_id).execute()

def fetch_data_and_store(sp, user_id):
    tracks = fetch_top_tracks(sp)
    refresh_user_tracks(user_id, tracks)
    update_last_fetched(user_id)


def load_user_tracks(user_id):
    return (
        supabase.table("user_tracks")
        .select("*")
        .eq("user_id", user_id)
        .order("rank")
        .execute().data
    )

def delete_user_data(user_id):
    supabase.table("user_tracks").delete().eq("user_id", user_id).execute()
    supabase.table("user_profiles").delete().eq("user_id",user_id).execute()
