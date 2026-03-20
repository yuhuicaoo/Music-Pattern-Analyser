import streamlit as st
from spotify_auth import get_spotify_client, show_login, show_consent
from spotify_data import fetch_data_and_store
from ui import show_tracks

def main():
    st.title("Spotify Top Tracks Collector")

    if "token" not in st.query_params:
        show_login()
        return

    st.session_state.setdefault("consent_given", False)
    st.session_state.setdefault("data_fetched", False)

    if not st.session_state.consent_given:
        show_consent()
        return

    sp = get_spotify_client()
    username = sp.me()["display_name"]
    st.success(f"Hello {username}!")

    if not st.session_state.data_fetched:
        fetch_data_and_store(sp, username)
        st.session_state.data_fetched = True

    show_tracks(username)

if __name__=="__main__":
    main()