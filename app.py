import streamlit as st
from auth import (
    get_spotify_client,
    get_returning_user,
    get_token_from_session,
    login_user,
    show_login,
)

from data import fetch_data_and_store
from ui import (
    show_disconnect_button,
    show_top_artists, 
    show_users,
    show_my_tracks
)


def main():
    st.markdown("""
        <style>
            h1 { margin-bottom: 0rem; }
        </style>
    """, unsafe_allow_html=True)

    token_info = get_token_from_session()
    if token_info:
        user_id = login_user(token_info)
        sp = get_spotify_client(user_id)
        fetch_data_and_store(sp, user_id)
        st.rerun()

    # check if already logged in
    user_id, display_name = get_returning_user()
    
    if not user_id:
        show_login()
        return

    # logged in
    sp = get_spotify_client(user_id)
    
    st.title("Spotify Music Tracker")
    st.caption(f"Logged in as **{display_name}**")
    show_disconnect_button(user_id)

    tab1, tab2, tab3 = st.tabs(["My Top Tracks", "My Top Artists", "Users"])

    with tab1:
        show_my_tracks(sp, user_id)
    with tab2:
        show_top_artists(user_id)
    with tab3:
        show_users()

if __name__ == "__main__":
    main()
