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

    user = sp.me()
    username = user["display_name"]
    st.success(f"Hello {username}!")

    # Fetch data
    results = sp.current_user_top_tracks(limit=50)
    for idx, track in enumerate(results["items"]):
        supabase.table("user_tracks").insert({
            "username": username,
            "track_id": track['id'],
            "track_name": track['name'],
            "artist": track['artists'][0]['name'],
        }).execute()
    
    st.success(f"Saved {len(idx)} tracks to Supabase!")

    data = supabase.table("user_tracks").select("*").eq("username", username).execute()
    df = pd.DataFrame(data.data)
    st.dataframe(df)
else:
    st.info("Please log in with Spotify")