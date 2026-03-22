import streamlit as st
import streamlit.components.v1 as components
from html import escape
from data import fetch_data_and_store, load_user_tracks, delete_user_data, needs_refresh
from config import cookie, supabase

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
    image_url = row["image_url"]
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

def show_my_tracks(sp, user_id):
    existing_data = load_user_tracks(user_id)

    if existing_data and not needs_refresh(user_id):
        show_tracks(user_id, existing_data)
        return
    
    # if new user (no existing data)
    st.session_state.setdefault("consent_given", False)
    if not st.session_state.consent_given:
        show_consent()
        return

    fetch_data_and_store(sp, user_id)
    show_tracks(user_id)

def show_tracks(user_id, tracks=None):
    if tracks is None:
        tracks = load_user_tracks(user_id)

    st.subheader("Your Top 50 Tracks This Month")
    cards = "".join(build_track_card(idx, row) for idx, row in enumerate(tracks))
    components.html(f"{TRACKS_CSS}<div>{cards}</div>", height=480, scrolling=True)

    st.markdown("""
        <style>
            div[data-testid="stExpander"] {
                margin-top: 4px;
                margin-bottom: 0px
            }
        </style>
    """, unsafe_allow_html=True)

def show_disconnect_button():
    with st.expander("Disconnect Spotify Account"):
        st.warning(
            "This will permanently delete all your data from our database, "
            "including your top tracks history. This cannot be undone."
        )
        confirm = st.checkbox("I understand this will delete all my data")
        if st.button("Delete my data and disconnect", type="primary"):
            if confirm:
                delete_user_data(st.session_state.user_id)
                if cookie.get("user_id"):
                    cookie.remove("user_id")
                # clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.query_params.clear()
                st.rerun()

def load_all_users():
    return (
        supabase.table("user_profiles")
        .select("display_name, profile_img")
        .execute().data
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
            font-size: 12px;
            color: #aaa;
            text-align: center;
            font-family: Inter, sans-serif;
        }
    </style>
    <div class="users-container">
    """

    for user in users:
        display_name = user['display_name']
        profile_img = user['profile_img']
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
