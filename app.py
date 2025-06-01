import streamlit as st
from supabase import create_client, Client
import time

SUPABASE_URL = st.secrets['SUPABASE_URL']
SUPABASE_KEY = st.secrets['SUPABASE_KEY']
BUCKET_NAME = 'push-files'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("PNR File Uploader with Upload Logging")

uploaded_file = st.file_uploader("Upload your PNR file (CSV, XML, JSON)", type=['csv', 'xml', 'json'])

if uploaded_file is not None:
    st.success(f"✅ File ready: {uploaded_file.name}")
    file_content = uploaded_file.read()
    unique_name = f"{int(time.time())}_{uploaded_file.name}"

    if st.button("Upload to Supabase"):
        try:
            res = supabase.storage.from_(BUCKET_NAME).upload(
                unique_name,
                file_content
            )

            if res.error:
                status = 'failed'
                error_message = str(res.error)
                st.error(f"❌ Upload failed: {error_message}")
                st.write("NOTE > Upload response:", res)
                
            else:
                status = 'success'
                error_message = None
                st.success(f"✅ Uploaded as `{unique_name}`!")
                st.write("NOTE > Upload response:", res)
                
        except Exception as e:
            status = 'failed'
            error_message = str(e)
            st.error("❌ Unexpected error during upload.")
            st.write("⚠ Exception details:", error_message)

        # ✅ Log the result into the Supabase Postgres table
        try:
            log_res = supabase.table('upload_logs').insert({
                'filename': uploaded_file.name,
                'unique_name': unique_name,
                'status': status,
                'error_message': error_message
            }).execute()

            if log_res.data:
                st.info("📝 Upload log saved to database.")
            else:
                st.warning("⚠ Failed to log upload to database.")

        except Exception as log_error:
            st.warning(f"⚠ Logging to database failed: {str(log_error)}")
