import streamlit as st
from supabase import create_client, Client
import os 

# Supabase credentials (you can set these as Streamlit secrets later)
SUPABASE_URL = 'https://quxsczncwedcxxflwyhh.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF1eHNjem5jd2VkY3h4Zmx3eWhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzMzk0MzIsImV4cCI6MjA2MzkxNTQzMn0.XhpqxgIic9mNEd2pxhsztZ-WaL5x2zngozbHUld2Wco'
BUCKET_NAME = 'push-files'

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("PNR Analyzer (with Supabase Storage)")

uploaded_file = st.file_uploader("Upload your PNR file (CSV, XML, JSON)", type=['csv', 'xml', 'json'])

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    file_content = uploaded_file.read()
    st.write(f"File size: {len(file_content)} bytes")

    # Upload to Supabase
    if st.button("Upload to Supabase"):
        file_path = f"{uploaded_file.name}"

        # Upload file to bucket
        response = supabase.storage.from_(BUCKET_NAME).upload(file_path, file_content)

        if response.get('error') is None:
            st.success(f"✅ File uploaded to Supabase bucket `{BUCKET_NAME}`!")
        else:
            st.error(f"❌ Upload failed: {response.get('error')['message']}")
