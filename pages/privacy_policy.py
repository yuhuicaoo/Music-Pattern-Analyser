import streamlit as st
from config import BACKEND_URL

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
    st.markdown(f'''
        <a href="{BACKEND_URL}/login" target="_self" style="
            display: inline-block;
            background-color: #1DB954;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
        ">I agree, Login with Spotify</a>
    ''', unsafe_allow_html=True)