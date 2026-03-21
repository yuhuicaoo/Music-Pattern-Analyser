import streamlit as st
import datetime

def show_privacy_policy():
    st.title("Privacy Policy")
    st.markdown(f"""
    **Last updated: {datetime.now().strftime("%B %Y")}**

    ### What we collect
    - Your Spotify display name, profile image, and user ID
    - Your top 50 tracks each month including track name and artist

    ### Why we collect it
    We collect this data solely to display your top tracks and compare 
    them with other users in the app.

    ### How long we keep it
    We only store your current month's data. When you log in each month 
    your previous data is replaced with your new top tracks.

    ### Your rights
    You can delete all your data at any time using the disconnect button 
    at the bottom of the main page. Your data will be permanently deleted 
    within 5 days of your request.

    ### Third parties
    Your data is stored in Supabase. It is never sold or shared with 
    any third party for advertising or any other purpose.

    ### Contact
    If you have any questions email us at [your email here]
    """)

show_privacy_policy()