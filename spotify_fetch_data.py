import pandas as pd

def fetch_top_tracks(sp, limit=50):
    results = sp.current_user_top_tracks(limit=limit)
    tracks = []
    for item in results['items']:
        tracks.append({
            "track_id": item['id'],
            "artist": item['artists'][0]['name'],
            "track_name": item['name'],
    })
    df = pd.DataFrame(tracks)
    return df