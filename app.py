import streamlit as st
from supabase import create_client, Client
import time
import os
import xml.etree.ElementTree as ET


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
    st.success(f"✅ File ready: {uploaded_file.name}")
    # st.success(f"✅ File ready")
    
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
                st.success(f"✅ Uploaded as V2 `{unique_name}`!")
                # st.success(f"✅ Uploaded")
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
            #    'error_message': error_message if error_message is not None else '',
            #})
            
            
            log_res = supabase.table('upload_logs').insert({
                'filename': uploaded_file.name,
                'unique_name': unique_name,
                'status': status,
                'error_message': error_message,
                'user_ip': 'unknown'
            }).execute()
        
            # Safely display log response
            log_res_dict = log_res.__dict__
            if log_res_dict.get('data'):
               st.info("📝 Upload log saved to database.")
               # st.info(f"✅ Ready for processing.")
            else:
                st.warning("⚠ Failed to log upload to database.")
                st.write("Log response details:", log_res_dict)

        except Exception as log_error:
            st.warning(f"⚠ Logging to database failed V2: {str(log_error)}")

#####################################################################################
# NEW SECTION: Load question_map.xml from Supabase Storage
#####################################################################################

try:
    TOPIC_BUCKET = 'topic.map'
    TOPIC_FILE = 'question_map.xml'

    ref_file_res = supabase.storage.from_(TOPIC_BUCKET).download(TOPIC_FILE)
    xml_content = ref_file_res.decode('utf-8')

    root = ET.fromstring(xml_content)
    questions_data = {}
    for topic in root.findall('topic'):
        topic_name = topic.get('name')
        questions_data[topic_name] = []

        for question in topic.findall('question'):
            text = question.find('text').text
            prompts = [p.text for p in question.find('prompts').findall('prompt')]
            agent_name = question.find('agent_name').text

            questions_data[topic_name].append({
                'text': text,
                'prompts': prompts,
                'agent_name': agent_name
            })

    st.info("✅ Loaded question_map.xml successfully")
    #st.write("📦 Loaded Questions Map:", questions_data)
    st.write("📦 Loaded Questions Map.")

except Exception as e:
    st.warning("⚠ Failed to load question_map.xml from Supabase Storage.")
    st.write("Exception details:", str(e))

#######################################################################################
########################################## agent AI ###################################

import openai
import json
import pandas as pd

# Set OpenAI API key
openai.api_key = st.secrets['OPENAI_API_KEY']

# Check if a file was uploaded
if uploaded_file is not None:
    st.info("🚀 Sending uploaded file to AI agent for passenger extraction...")

    try:
        # Read and decode the file content
        file_content = uploaded_file.read().decode('utf-8')


        #######################################################################################
        # Build the prompt

        prompt = f"""
You are an expert at reading airline booking files (PNRs).
Given the following file content, extract:

1. A header section that dynamically includes **any and all details common to all passengers**.
For example: flight number, airline, route, departure time, arrival time, aircraft type, aircraft manufacturer, pilot name — 
or any other shared details found.

2. A passenger list section with: PNR Reference, Name, Surname, Date of Birth, Seat Number.

File content:
{file_content}

Output as JSON object:
{{
    "header": {{
        <key>: <value>,
        <key>: <value>,
        ...
    }},
    "passengers": [
        {{"pnr_reference": "...", "name": "...", "surname": "...", "dob": "...", "seat_number": "..."}},
        ...
    ]
}}
Only include fields in the header if they actually appear in the file.
        """
        ####################################################################################
        # Send to OpenAI GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # Parse GPT response
        response_text = response['choices'][0]['message']['content']
        parsed_result = json.loads(response_text)

        header = parsed_result['header']
        passenger_list = parsed_result['passengers']

        # Display header dynamically
        st.subheader("✈ Flight Details (All Shared Info)")
        for key, value in header.items():
            st.write(f"**{key}**: {value}")

        # Display passengers
        import pandas as pd
        df = pd.DataFrame(passenger_list)
        st.subheader("🧳 Passenger List")    
        st.dataframe(df)

    except Exception as e:
        st.write("Exception ...")
