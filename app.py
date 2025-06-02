import streamlit as st
from supabase import create_client, Client
import time
import os


# Load Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets['SUPABASE_URL']
SUPABASE_KEY = st.secrets['SUPABASE_KEY']
BUCKET_NAME = 'push-files'

# Connect to Supabase
#####################################################################################
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔍 Debug: Check current database role
#####################################################################################
try:
    role_res = supabase.rpc('get_current_role').execute()
    # st.write("🔍 Current DB role (from Supabase):", role_res.data)
except Exception as e:
    st.warning("⚠ Could not fetch current DB role.")
    st.write("Exception details:", str(e))

# App title
st.title("Uploader V0")

# File upload section
uploaded_file = st.file_uploader("file (CSV, XML, JSON)", type=['csv', 'xml', 'json'])

if uploaded_file is not None:
    # st.success(f"✅ File ready: {uploaded_file.name}")
    st.success(f"✅ File ready")
    
    file_content = uploaded_file.read()
    unique_name = f"{int(time.time())}_{uploaded_file.name}"

    if True:    ########## st.button("Upload now"):
        try:
            # Upload to Supabase Storage
            res = supabase.storage.from_(BUCKET_NAME).upload(unique_name, file_content)
            res_dict = res.__dict__

            if res_dict.get('error'):
                status = 'failed'
                error_message = str(res_dict['error'])
                st.error(f"❌ Upload failed: {error_message}")
            else:
                status = 'success'
                error_message = None
                # st.success(f"✅ Uploaded as V2 `{unique_name}`!")
                st.success(f"✅ Uploaded")
        except Exception as e:
            status = 'failed'
            error_message = str(e)
            st.error("❌ Unexpected error during upload.")
            st.write("⚠ Exception details:", error_message if error_message is not None else '')

        # Log the result into the Supabase Postgres table
        try:
            
            #st.write("🚨 Insert payload going to Supabase:", {
            #    'filename': uploaded_file.name,
            #    'unique_name': unique_name,
            #    'status': status,
            #    'error_message': error_message if error_message is not None else ''
            #})
            
            
            log_res = supabase.table('upload_logs').insert({
                'filename': uploaded_file.name,
                'unique_name': unique_name,
                'status': status,
                'error_message': error_message
            }).execute()
        
            # Safely display log response
            log_res_dict = log_res.__dict__
            if log_res_dict.get('data'):
               # st.info("📝 Upload log saved to database.")
               st.info(f"✅ Ready for processing.")
            else:
                st.warning("⚠ Failed to log upload to database.")
                st.write("Log response details:", log_res_dict)

        except Exception as log_error:
            st.warning(f"⚠ Logging to database failed V2: {str(log_error)}")
