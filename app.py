import streamlit as st
from auth import (
    get_spotify_client,
    get_returning_user,
    save_user_session,
    show_login,
    get_spotify_client_for_user,
)

from ui import (
    show_consent,
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
    st.title("Spotify Top Tracks & Artists Collector")

    user_id, display_name = get_returning_user()

    if not user_id and "token" not in st.query_params:
        show_login()
        return

    if not user_id:
        sp = get_spotify_client()
        save_user_session(sp)
        user_id, display_name = get_returning_user()
    
    st.subheader(f"Hello {display_name}!")

    st.session_state.setdefault("consent_given", False)
    if not st.session_state.consent_given:
        show_consent()
        show_disconnect_button()
        return

    tab1, tab2, tab3 = st.tabs(["My Top Tracks", "My Top Artists", "Current Users"])

    with tab1:
        sp = get_spotify_client_for_user(user_id)
        show_my_tracks(sp, user_id)
    with tab2:
        show_top_artists(user_id)
    with tab3:
        show_users()

    show_disconnect_button()

if __name__ == "__main__":
    main()
