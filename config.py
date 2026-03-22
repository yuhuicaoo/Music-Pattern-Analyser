import streamlit as st
from supabase import create_client

BACKEND_URL = st.secrets["app"]["BACKEND_URL"]

SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

supabase = create_client(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)