import streamlit as st
import pandas as pd
import spotipy
from fastapi.responses import RedirectResponse

# Streamlit UI
st.title("Spotify Top Tracks Collector")

backend_url = "https://music-pattern-analyser.onrender.com"

st.markdown(f"[Login with Spotify]({backend_url}/login)")

query_params = st.query_params

if "token" in query_params:
    access_token = query_params["token"]

    sp = spotipy.Spotify(auth = access_token)

    user = sp.me()
    username = user["display_name"]
    st.success(f"Hello {username}!")

    # Fetch data
    results = sp.current_user_top_tracks(limit=50)
    tracks = [{
        "track_id": track['id'],
        "artist": track['artists'][0]['name'],
        "track_name": track['name']
    } for track in results['items']]

    df = pd.DataFrame(tracks)
    st.dataframe(df)

    # CSV download
    csv_file = f"{username}_top50_tracks.csv"
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name=csv_file,
        mime="text/csv"
    )
else:
    st.info("Please log in with Spotify")