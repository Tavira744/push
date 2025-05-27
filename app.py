import streamlit as st
from supabase import create_client, Client
import os
import time


SUPABASE_URL = st.secrets['SUPABASE_URL']
SUPABASE_KEY = st.secrets['SUPABASE_KEY']
BUCKET_NAME = 'pnr-files'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

uploaded_file = st.file_uploader("Upload your PNR file (CSV, XML, JSON)", type=['csv', 'xml', 'json'])

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    file_content = uploaded_file.read()

    # Create unique filename
    unique_name = f"{int(time.time())}_{uploaded_file.name}"

    if st.button("Upload to Supabase"):
        res = supabase.storage.from_(BUCKET_NAME).upload(
            unique_name,
            file_content
        )

        if res.data:
            st.success(f"✅ File uploaded as `{unique_name}` to Supabase!")
        else:
            st.error(f"❌ Upload failed: {res.error}")
