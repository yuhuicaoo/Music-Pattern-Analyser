import streamlit as st
from auth import (
    get_spotify_client,
    get_returning_user,
    save_user_session,
    show_login,
    show_consent,
)
from data import fetch_data_and_store, already_fetched_this_month
from ui import show_tracks


def main():
    st.title("Spotify Top Tracks Collector")

    user_id, display_name = get_returning_user()

    if not user_id and "token" not in st.query_params:
        show_login()
        return

    if not user_id:
        sp = get_spotify_client()
        save_user_session(sp)
        user_id, display_name = get_returning_user()

    st.success(f"Hello {display_name}!")

    st.session_state.setdefault("consent_given", False)

    if not st.session_state.consent_given:
        show_consent()
        return
    
    if not already_fetched_this_month(user_id):
        sp = get_spotify_client()
        fetch_data_and_store(sp, user_id)

    with st.spinner("Displaying your top tracks this month"):
        show_tracks(user_id)



if __name__ == "__main__":
    main()
