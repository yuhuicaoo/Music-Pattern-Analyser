import streamlit as st

def save_csv(df, username):
    filename = f"{username}_top50_tracks.csv"
    df.to_csv(filename, index=False)
    return filename

