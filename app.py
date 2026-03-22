import streamlit as st
from auth import (
    get_spotify_client,
    get_returning_user,
    save_user_session,
    show_login,
    show_consent,
    get_spotify_client_for_user,
)
from data import (
    fetch_data_and_store, 
    needs_refresh, 
    load_user_tracks
)

from ui import show_tracks, show_disconnect_button


def main():
    st.markdown("""
        <style>
            h1 { margin-bottom: 0rem; }
        </style>
    """, unsafe_allow_html=True)
    st.title("Spotify Top Tracks Collector")

    user_id, display_name = get_returning_user()

    if not user_id and "token" not in st.query_params:
        show_login()
        return

    if not user_id:
        sp = get_spotify_client()
        save_user_session(sp)
        user_id, display_name = get_returning_user()
    
    st.subheader(f"Hello {display_name}!")

    sp = get_spotify_client_for_user(user_id)

    # check if user has existing data
    existing_data = load_user_tracks(user_id)

    if existing_data and not needs_refresh(user_id):
        show_tracks(user_id, display_name, existing_data)
        show_disconnect_button()
        return

    # if new user (no existing data)
    st.session_state.setdefault("consent_given", False)
    if not st.session_state.consent_given:
        show_consent()
        return

    fetch_data_and_store(sp, user_id)
    show_tracks(user_id, display_name)
    show_disconnect_button()

if __name__ == "__main__":
    main()
