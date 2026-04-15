import streamlit as st
import requests


if 'history_log' not in st.session_state:
    st.session_state.history_log = []

st.set_page_config(page_title="Aadhaar Fraud Shield", layout="centered")

st.title("🛡️ Aadhaar Fraud Detection System")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Aadhaar Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:

    if st.button("Verify Document"):
        with st.spinner("Analyzing document..."):

            files = {"file": uploaded_file.getvalue()}

            try:
                response = requests.post("http://127.0.0.1:8000/verify", files=files)
                res = response.json()

                st.markdown("---")

                # Authenticity
                if res['fraud_result'] == "Tampered":
                    st.error(f"🔍 AUTHENTICITY: {res['fraud_result']}")
                else:
                    st.success(f"✅ AUTHENTICITY: {res['fraud_result']}")

                # Masked Aadhaar
                st.info(f"🆔 Masked ID: {res['masked_id']}")

                # Final status
                if res['final_status'] == "VERIFIED":
                    st.success("🏁 FINAL VERDICT: KYC APPROVED")
                else:
                    st.error("🏁 FINAL VERDICT: KYC REJECTED")

                st.caption(f"Processed at: {res['timestamp']}")

                # Add to history
                log_entry = {
                    "Time": res['timestamp'],
                    "Filename": uploaded_file.name,
                    "Aadhaar ID": res['masked_id'],
                    "Status": res['final_status']
                }

                st.session_state.history_log.insert(0, log_entry)

            except:
                st.error("Error: Backend not running")


if st.session_state.history_log:
    st.write("---")
    st.subheader("📜 Verification History")
    st.table(st.session_state.history_log)

    if st.button("Clear History"):
        st.session_state.history_log = []
        st.rerun()