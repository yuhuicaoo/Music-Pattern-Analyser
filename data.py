import streamlit as st
from datetime import datetime
from config import supabase


def fetch_and_save_top_tracks(sp, user_id):
    top_tracks = sp.current_user_top_tracks(limit=50, time_range="short_term")["items"]
    tracks = [
        {
            "user_id": user_id,
            "track_id": track["id"],
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],
            "rank": idx + 1,
            "image_url": track["album"]["images"][0]["url"],
            "track_url": track["external_urls"]["spotify"]
        }
        for idx, track in enumerate(top_tracks)
    ]
    supabase.table("user_tracks").upsert(tracks, on_conflict="user_id,rank").execute()


def fetch_and_save_top_artists(sp, user_id):
    top_artists = sp.current_user_top_artists(limit=5, time_range="short_term")["items"]
    artists = [
        {
            "user_id": user_id,
            "artist_id": artist["id"],
            "artist_name": artist["name"],
            "rank": idx + 1,
            "image_url": artist["images"][0]["url"],
            "artist_url": artist["external_urls"]["spotify"]
        }
        for idx, artist in enumerate(top_artists)
    ]
    supabase.table("user_artists").upsert(artists, on_conflict="user_id, rank").execute()

def fetch_data_and_store(sp, user_id):
    if needs_refresh(user_id):
        fetch_and_save_top_tracks(sp, user_id)
        fetch_and_save_top_artists(sp, user_id)
        update_last_fetched(user_id)

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

def load_user_tracks(user_id):
    return (
        supabase.table("user_tracks")
        .select("*")
        .eq("user_id", user_id)
        .order("rank")
        .execute().data
    )

def load_user_artists(user_id):
    return (
        supabase.table("user_artists")
        .select("*")
        .eq("user_id", user_id)
        .order("rank")
        .execute().data
    )

def delete_user_data(user_id):
    supabase.table("user_profiles").delete().eq("user_id", user_id).execute()

def load_all_users_top5_tracks():
    users = (
        supabase.table("user_profiles")
        .select("user_id, display_name, profile_img")
        .execute().data
    )
    
    results = []
    for user in users:
        user_top5_tracks = (
            supabase.table("user_tracks")
            .select("*")
            .eq("user_id", user["user_id"])
            .order("rank")
            .limit(5)
            .execute().data
        )

        results.append({
            "user": user,
            "tracks": user_top5_tracks,
        })
    return results