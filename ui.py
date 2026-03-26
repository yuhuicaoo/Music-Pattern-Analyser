import streamlit as st
import streamlit.components.v1 as components
from html import escape
from auth import logout_user
from data import (
    fetch_data_and_store,
    load_all_users_top5_tracks,
    load_user_artists,
    load_user_tracks,
    needs_refresh,
)
from config import BACKEND_URL, supabase

TRACKS_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
    body { margin: 0; padding: 12px; background-color: #111; font-family: 'Inter', sans-serif; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #111; }
    ::-webkit-scrollbar-thumb { background: #444; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #666; }
    .track-card {
        display: flex;
        align-items: center;
        padding: 10px;
        margin-bottom: 8px;
        background-color: #1a1a1a;
        border-radius: 10px;
        transition: background-color 0.2s;
        cursor: pointer;

    }
    .track-card:hover { background-color: #2a2a2a; }
    .track-number { font-size: 14px; color: #888; width: 30px; text-align: center; }
    .track-image { width: 50px; height: 50px; border-radius: 5px; margin: 0 15px; }
    .track-name { font-size: 15px; font-weight: bold; color: white; }
    .track-artist { font-size: 13px; color: #aaa; }
</style>
"""


def build_track_card(idx, row):
    image_url = row["image_url"]
    track_name = escape(row["track_name"])
    artist = escape(row["artist"])
    track_url = row["track_url"]

    return f"""
        <a href="{track_url}" target="_blank" style="text-decoration: none;">
            <div class="track-card">
                <span class="track-number">{idx + 1}</span>
                <img class="track-image" src="{image_url}" />
                <div>
                    <div class="track-name">{track_name}</div>
                    <div class="track-artist">{artist}</div>
                </div>
            </div>
        </a>
    """


def show_my_tracks(sp, user_id):
    existing_data = load_user_tracks(user_id)

    if existing_data and not needs_refresh(user_id):
        show_tracks(user_id, existing_data)
        return

    fetch_data_and_store(sp, user_id)
    show_tracks(user_id)


def show_tracks(user_id, tracks=None):
    if tracks is None:
        tracks = load_user_tracks(user_id)

    st.subheader(f"Your Top {len(tracks)} Tracks This Month")
    cards = "".join(build_track_card(idx, row) for idx, row in enumerate(tracks))
    components.html(f"{TRACKS_CSS}<div>{cards}</div>", height=400, scrolling=True)

    st.markdown(
        """
        <style>
            div[data-testid="stExpander"] {
                margin-top: 4px;
                margin-bottom: 0px
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


def show_disconnect_button(user_id):
    if st.button("Disconnect and Logout"):
        logout_user(user_id)
        st.rerun()

def show_login_button():
    st.title("🎵 Music Tracker")
    st.caption("Login to see your top Spotify tracks alongside your friends.")
    if st.button("Login with Spotify", type="primary"):
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={BACKEND_URL}/login">',
            unsafe_allow_html=True,
        )

def load_all_users():
    return (
        supabase.table("user_profiles")
        .select("display_name, profile_img")
        .execute()
        .data
    )
    
def show_users():
    users = load_all_users()
    if not users:
        return

    st.subheader(f"Current Users: {len(users)}")

    users_html = """
    <style>
        .users-container {
            display: flex;
            flex-direction: row;
            gap: 16px;
            overflow-x: auto;
            padding: 10px 0;
        }
        .user-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            min-width: 80px;
        }
        .user-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
        }
        .user-avatar-placeholder {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        .user-name {
            font-size: 16px;
            color: white;
            text-align: center;
            font-family: Inter, sans-serif;
            font-weight: bold
        }
    </style>
    <div class="users-container">
    """

    for user in users:
        display_name = user["display_name"]
        profile_img = user["profile_img"]
        placeholder_img = display_name[0].upper()

        if profile_img:
            avatar = f'<img class="user-avatar" src="{profile_img}" />'
        else:
            avatar = f'<div class="user-avatar-placeholder">{placeholder_img}</div>'

        users_html += f"""
            <div class="user-card">
                {avatar}
                <div class="user-name">{display_name}</div>
            </div>
        """

    users_html += "</div>"
    components.html(users_html, height=120)


def show_consent():
    st.warning(
        "Do you agree to giving access to your Spotify listening data and storing it in our database?"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, I consent", use_container_width=True):
            st.session_state.consent_given = True
            st.rerun()
    with col2:
        if st.button("No, I do not give consent", use_container_width=True):
            st.info("Your data will not be accessed or stored")
            st.stop()


def show_top_artists(user_id):
    artists = load_user_artists(user_id)
    if not artists:
        return

    st.subheader(f"Your Top {len(artists)} Artists This Month")

    artists_html = """
    <style>
        .artists-container {
            display: flex;
            flex-direction: row;
            justify-content: space-between
            width: 100%;
            padding: 10px 0;
        }
        .artist-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            flex: 1;
        }
        .artist-image {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            transition: opacity 0.2s;
        }
        .artist-image:hover {
            opacity: 0.8;  /* 👈 dims on hover */
        }
        .artist-rank {
            font-size: 20px;
            color: white;
            font-family: Inter, sans-serif;
            font-weight: bold;
        }
        .artist-name {
            font-size: 16px;
            color: white;
            text-align: center;
            font-family: Inter, sans-serif;
            font-weight: bold;
        }
    </style>
    <div class="artists-container">
    """

    for artist in artists:
        img = artist.get("image_url", "")
        name = artist["artist_name"]
        rank = artist["rank"]
        artist_url = artist["artist_url"]

        artists_html += f"""
            <div class="artist-card">
                <div class="artist-rank">#{rank}</div>
                <a href="{artist_url}" target="_blank">
                    <img class="artist-image" src="{img}" />
                </a>
                <div class="artist-name">{name}</div>
            </div>
        """

    artists_html += "</div>"
    components.html(artists_html, height=200)


def show_all_users_tracks():
    data = load_all_users_top5_tracks()

    if not data:
        st.info("No users yet.")
        return
    
    st.subheader("Compare your Top 5 Tracks")

    for i in range(0, len(data), 2):
        chunk = data[i:i+2]
        cols = st.columns(2)

        for col, user_data in zip(cols, chunk):
            user = user_data["user"]
            tracks = user_data["tracks"]

            with col:
                display_name = user["display_name"]

                cards = f"""
                    <div style="font-size: 15px; font-weight: bold; color: white; 
                        font-family: Inter, sans-serif; margin-bottom: 8px;">
                        {display_name}
                    </div>
                """
                for idx, row in enumerate(tracks):
                    image_url = row["image_url"]
                    track_name = escape(row["track_name"])
                    artist = escape(row["artist"])
                    track_url = row.get("track_url", "#")

                    cards += f"""
                        <a href="{track_url}" target="_blank" style="text-decoration: none;">
                            <div class="track-card">
                                <span class="track-number">{idx + 1}</span>
                                <img class="track-image" src="{image_url}" />
                                <div>
                                    <div class="track-name">{track_name}</div>
                                    <div class="track-artist">{artist}</div>
                                </div>
                            </div>
                        </a>
                    """
                components.html(f"{TRACKS_CSS}<div>{cards}</div>", height=410, scrolling=False)