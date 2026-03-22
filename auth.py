import spotipy
import streamlit as st
from config import supabase, BACKEND_URL, cookie, sp_oauth
from datetime import datetime
from ui import show_users
import requests

@st.dialog("Privacy Policy")
def show_privacy_policy_modal():
    st.markdown(
        """
    ### What we collect
    - Your Spotify display name and user ID
    - Your top 50 tracks each month including track name and artist

    ### Why we collect it
    Solely to display your top tracks and compare them with other users.

    ### How long we keep it
    Only your current data is stored. It is replaced each time you log in.

    ### Your rights
    You can delete all your data at any time using the disconnect button 
    on the main page.

    ### Third parties
    Your data is stored in Supabase. It is never sold or shared with 
    any third party.
    """
    )
    # login button lives inside the modal
    st.markdown(
        f"""
        <a href="{BACKEND_URL}/login" style="
            display: inline-block;
            background-color: #1DB954;
            width: 100%;
            color: white;
            padding: 8px 24px;
            border-radius: 16px;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
        ">I agree, Login with Spotify</a>
    """,
        unsafe_allow_html=True,
    )


def get_spotify_client():

    if "token_info" in st.session_state:
        return spotipy.Spotify(auth=st.session_state.token_info["access_token"])

    key = st.query_params.get("session")
    if not key:
        return None

    if isinstance(key, list):
        key = key[0]

    response = requests.get(f"{BACKEND_URL}/token/{key}")
    token_info = response.json()
    if "error" in token_info:
        return None

    st.session_state.token_info = token_info
    return spotipy.Spotify(auth=token_info["access_token"])


def save_user_session(sp):
    user = sp.me()
    user_id = user["id"]
    display_name = user["display_name"]
    profile_img = user["images"][0]["url"]

    # convert unix timestamp to isoformat
    token_info = st.session_state.token_info
    expires_at = datetime.fromtimestamp(token_info["expires_at"]).isoformat()

    # insert user data into database
    supabase.table("user_profiles").upsert(
        {
            "user_id": user_id,
            "display_name": display_name,
            "access_token": token_info["access_token"],
            "refresh_token": token_info["refresh_token"],
            "token_expiry": expires_at,
            "profile_img": profile_img,
        },
        on_conflict="user_id",
    ).execute()

    cookie.set("user_id", user_id)
    st.session_state.user_id = user_id
    st.session_state.display_name = display_name


def get_spotify_client_for_user(user_id):
    profile = (
        supabase.table("user_profiles")
        .select("access_token, refresh_token, token_expiry")
        .eq("user_id", user_id)
        .single()
        .execute()
        .data
    )

    token_expiry = datetime.fromisoformat(profile["token_expiry"])

    if datetime.now() > token_expiry:
        # token expired, need to refresh token
        token_info = sp_oauth.refresh_access_token(profile["refresh_token"])

        new_expiry = new_expiry = datetime.fromtimestamp(
            token_info["expires_at"]
        ).isoformat()

        supabase.table("user_profiles").update(
            {"access_token": token_info["access_token"], "token_expiry": new_expiry}
        ).eq("user_id", user_id).execute()

        return spotipy.Spotify(auth=token_info["access_token"])

    return spotipy.Spotify(auth=profile["access_token"])


def get_returning_user():
    if "user_id" in st.session_state:
        return st.session_state.user_id, st.session_state.display_name

    user_id = cookie.get("user_id")
    if user_id:
        try:
            profile = (
                supabase.table("user_profiles")
                .select("display_name")
                .eq("user_id", user_id)
                .single()
                .execute()
                .data
            )
            if profile:
                st.session_state.user_id = user_id
                st.session_state.display_name = profile["display_name"]
                return user_id, profile["display_name"]
        except Exception:
            # cookie exists but user not in db, clear the cookie
            cookie.remove("user_id")

    return None, None


def show_login():
    st.subheader("Welcome!")
    st.caption("Login to see your top Spotify tracks.")
    if st.button("Login with Spotify", type="primary"):
        show_privacy_policy_modal()

    show_users()
