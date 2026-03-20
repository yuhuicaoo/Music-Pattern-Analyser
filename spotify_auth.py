import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "user-top-read"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
)

def get_auth_url():
    return sp_oauth.get_authorize_url()

def get_spotify_client(code):
    access_token = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=access_token)
    return sp
