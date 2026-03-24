import spotipy
import streamlit as st
from config import supabase, BACKEND_URL, make_sp_oauth
from datetime import datetime
import requests

from data import delete_user_data


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


def get_spotify_client(user_id):
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
        token_info = make_sp_oauth.refresh_access_token(profile["refresh_token"])
        new_expiry = datetime.fromtimestamp(token_info["expires_at"]).isoformat()

        supabase.table("user_profiles").update(
            {
                "access_token": token_info["access_token"],
                "token_expiry": new_expiry,
            }
        ).eq("user_id", user_id).execute()
        return spotipy.Spotify(auth=token_info["access_token"])

    return spotipy.Spotify(auth=profile["access_token"])


def login_user(token_info):
    sp = spotipy.Spotify(auth=token_info["access_token"])
    user = sp.me()
    user_id = user["id"]
    display_name = user["display_name"]
    profile_img = user["images"][0]["url"] if user.get("images") else None

    # convert unix timestamp to isoformat
    expires_at = datetime.fromtimestamp(token_info["expires_at"]).isoformat()

    # store user data into database
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

    st.session_state.user_id = user_id
    st.session_state.display_name = display_name

    return user_id


def get_token_from_session():
    key = st.query_params.get("session")
    if not key:
        return None, None

    response = requests.get(f"{BACKEND_URL}/token/{key}").json()
    st.query_params.clear()

    if "error" in response:
        return None, None

    return response["token_info"], response["user_id"]


def get_returning_user():
    user_id = st.session_state.get("user_id")
    display_name = st.session_state.get("display_name")

    if not user_id:
        return None, None

    return user_id, display_name


def logout_user(user_id):
    delete_user_data(user_id)
    st.session_state.clear()


def show_login():
    st.subheader("Welcome!")
    st.caption("Login to see your top Spotify tracks.")
    if st.button("Login with Spotify", type="primary"):
        show_privacy_policy_modal()
