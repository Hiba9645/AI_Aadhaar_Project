import streamlit as st
import requests

st.set_page_config(page_title="Aadhaar Fraud Shield", layout="centered")

st.title("🛡️ Aadhaar Fraud Detection System")
st.markdown("---")


uploaded_file = st.file_uploader("Upload Aadhaar Image for Verification", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    
    if st.button("Verify Document"):
        with st.spinner("Analyzing document..."):
            files = {"file": uploaded_file.getvalue()}
            try:
                
                response = requests.post("http://127.0.0.1:8000/verify", files=files)
                res = response.json()

                st.markdown("---")
                
                
                if res['fraud_result'] == "Tampered":
                    st.error(f" AUTHENTICITY: {res['fraud_result']}")
                else:
                    st.success(f" AUTHENTICITY: {res['fraud_result']}")
                
                st.write("") 
                
                
                if res['final_status'] == "VERIFIED":
                    st.success("🏁 FINAL VERDICT: KYC APPROVED")
                else:
                    st.error("🏁 FINAL VERDICT: KYC REJECTED")
                    
                    
            except Exception as e:
                st.error("Error: Could not connect to the Backend. Please ensure Uvicorn is running.")