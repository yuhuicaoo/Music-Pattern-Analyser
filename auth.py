import spotipy
import streamlit as st
from config import supabase, BACKEND_URL


@st.dialog("Privacy Policy")
def show_privacy_policy_modal():
    st.markdown("""
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
    """)
    st.divider()
    # login button lives inside the modal
    st.link_button(
        "I agree, Login with Spotify",
        url=f"{BACKEND_URL}/login",
        use_container_width=True,
        type="primary"
    )

def get_spotify_client():
    return spotipy.Spotify(auth=st.query_params["token"])

def save_user_session(sp):
    user = sp.me()
    user_id = user['id']
    display_name = user['display_name']

    # insert user data into database
    supabase.table("user_profiles").upsert({
        "user_id": user_id,
        "display_name": display_name,
        "access_token": st.query_params["token"],
    }, on_conflict="user_id").execute()

    st.session_state.user_id = user_id
    st.session_state.display_name = display_name

def get_returning_user():
    if "user_id" in st.session_state:
        return st.session_state.user_id, st.session_state.display_name
    return None, None

def show_login():
    st.subheader("Welcome!")
    st.caption("Login to see your top Spotify tracks.")
    if st.button("Login with Spotify", type="primary"):
        show_privacy_policy_modal()

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

@st.dialog("Privacy Policy")
def show_privacy_policy_modal():
    st.markdown("""
    ### What we collect
    - Your Spotify display name, profile image, and user ID
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

    ### Contact
    [yuhuicao20@gmail.com]
    """)
    if st.button("Close", use_container_width=True):
        st.rerun()