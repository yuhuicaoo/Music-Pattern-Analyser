import streamlit as st
import streamlit.components.v1 as components
from html import escape
from utils import img_to_base64
from spotify_data import load_user_tracks

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
    }
    .track-card:hover { background-color: #2a2a2a; }
    .track-number { font-size: 14px; color: #888; width: 30px; text-align: center; }
    .track-image { width: 50px; height: 50px; border-radius: 5px; margin: 0 15px; }
    .track-name { font-size: 15px; font-weight: bold; color: white; }
    .track-artist { font-size: 13px; color: #aaa; }
</style>
"""

def build_track_card(idx, row):
    raw_img = st.session_state.track_imgs.get(row["track_id"], "")
    image_url = img_to_base64(raw_img)
    track_name = escape(row["track_name"])
    artist = escape(row["artist"])

    return f"""
        <div class="track-card">
            <span class="track-number">{idx + 1}</span>
            <img class="track-image" src="{image_url}" />
            <div>
                <div class="track-name">{track_name}</div>
                <div class="track-artist">{artist}</div>
            </div>
        </div>
    """

def show_tracks(username):
    with st.spinner("Loading your top 50 songs..."):
        tracks = load_user_tracks(username)

    st.subheader("Your Top 50 Tracks This Month")
    cards = "".join(build_track_card(idx, row) for idx, row in enumerate(tracks))
    components.html(f"{TRACKS_CSS}<div>{cards}</div>", height=520, scrolling=True)