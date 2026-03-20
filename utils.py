
import base64
import requests
import pandas as pd

def save_csv(df, username):
    filename = f"{username}_top50_tracks.csv"
    df.to_csv(filename, index=False)
    return filename

def img_to_base64(url):
    try:
        response = requests.get(url, timeout=5)
        encoded = base64.b64encode(response.content).decode("utf-8")
        mime = response.headers.get("Content-Type", "image/jpeg")
        return f"data:{mime};base64,{encoded}"
    except:
        return ""
