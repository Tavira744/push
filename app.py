import streamlit as st

st.title("PNR Analyzer (Prototype)")

uploaded_file = st.file_uploader("Upload your PNR file (CSV, XML, JSON)", type=['csv', 'xml', 'json'])

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    file_content = uploaded_file.read()
    st.write(f"File size: {len(file_content)} bytes")

    if st.button("Run Analysis"):
        st.write("👉 Agent analysis will go here.")
