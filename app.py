import spotipy
import pandas as pd
import streamlit as st
from supabase import create_client

SUPABASE_URL= st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

supabase = create_client(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY
)

# Streamlit UI
st.title("Spotify Top Tracks Collector")

backend_url = "https://music-pattern-analyser.onrender.com"

st.markdown(f'<a href="{backend_url}/login" target="_self">Login with Spotify</a>', unsafe_allow_html=True)

query_params = st.query_params

if "token" in query_params:
    access_token = query_params["token"]

    sp = spotipy.Spotify(auth = access_token)

    # Get username
    user = sp.me()
    username = user["display_name"]
    st.success(f"Hello {username}!")

    if "consent_given" not in st.session_state:
        st.session_state.consent_given = False

    if not st.session_state.consent_give:
        st.warning("Do you agree to giving access to your Spotify listening data and storing it in our database?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, I consent"):
                st.session_state.consent_given = True
                st.rerun()
        with col2:
            if st.button("No, I do not give consent"):
                st.info("Your data will not be accessed or stored")
                st.stop()
    else:
        # Fetch data from Spotify API and store in database
        with st.spinner("Fetching your top tracks from Spotify..."):
            results = sp.current_user_top_tracks(limit=50, time_range="short_term")
            for idx, track in enumerate(results["items"]):
                supabase.table("user_tracks").insert({
                    "username": username,
                    "track_id": track['id'],
                    "track_name": track['name'],
                    "artist": track['artists'][0]['name'],
                }).execute()
        

        # Fetch data from database
        with st.spinner("Loading your top 50 songs for this month"):
            data = supabase.table("user_tracks").select("*").eq("username", username).execute()
            df = pd.DataFrame(data.data)
            df = df.drop('id', axis=1)
        st.dataframe(df)
else:
    st.info("Please log in with Spotify")