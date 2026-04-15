import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
import pytesseract
import re
import platform
from PIL import Image
from datetime import datetime

# Initialize session state to store verification history
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@st.cache_resource
def load_my_model():
    try:
        return tf.keras.models.load_model("fraud_model.h5", compile=False)
    except Exception as e:
        st.error(f"Model Loading Error: {e}")
        return None

MODEL = load_my_model()

def milestone1_preprocess(img):
    img_resized = cv2.resize(img, (800, 500))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    sharpened = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

def run_fraud_detection(img):
    img_input = cv2.resize(img, (96, 96))
    img_scaled = img_input / 255.0
    img_batch = np.expand_dims(img_scaled, axis=0)
    prediction = MODEL.predict(img_batch)
    score = float(prediction[0][0])
    label = "Tampered" if score > 0.5 else "Original"
    return label, score

def run_ocr_with_masking(img):
    text = pytesseract.image_to_string(img)
    match = re.search(r'(\d{4}[\s.]?\d{4}[\s.]?\d{4}|\d{12})', text)
    if match:
        full_num = match.group(0).replace(" ", "").replace("-", "").replace(".", "")
        masked_num = f"XXXX-XXXX-{full_num[-4:]}"
        return True, masked_num
    return False, "Not Detected"

st.set_page_config(page_title="Aadhaar Fraud Shield", layout="centered")
st.title("🛡️ Aadhaar Fraud Detection System")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Aadhaar Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    img_display = Image.open(uploaded_file)
    st.image(img_display, caption="Uploaded Document Preview", width=300)
    if st.button("Verify Document"):
        with st.spinner("Analyzing..."):
            file_bytes = np.asarray(bytearray(uploaded_file.getvalue()), dtype=np.uint8)
            raw_img = cv2.imdecode(file_bytes, 1)
            processed_img = milestone1_preprocess(raw_img)
            fraud_label, fraud_score = run_fraud_detection(processed_img)
            # Feature 1: Masking
            has_aadhaar, masked_id = run_ocr_with_masking(processed_img)
            overall_status = "VERIFIED" if (fraud_label == "Original" and has_aadhaar) else "REJECTED"
            # Feature 2: Timestamp
            now = datetime.now().strftime("%H:%M:%S")
            # Feature 3: Add to History Log
            log_entry = {
                "Time": now,
                "Filename": uploaded_file.name,
                "Aadhaar ID": masked_id,
                "Status": overall_status
            }
            st.session_state.history_log.insert(0, log_entry) # Add new result at the top
            st.markdown("---")
            if fraud_label == "Tampered":
                st.error(f"🔍 AUTHENTICITY: {fraud_label}")
            else:
                st.success(f"✅ AUTHENTICITY: {fraud_label}")
            st.info(f"🆔 Masked ID: {masked_id}")
            if overall_status == "VERIFIED":
                st.success("🏁 FINAL VERDICT: KYC APPROVED")
            else:
                st.error("🏁 FINAL VERDICT: KYC REJECTED")
            st.caption(f"Processed at: {now}")

# Display the History Log at the bottom of the page
if st.session_state.history_log:
    st.write("---")
    st.subheader("📜 Session Verification History")
    st.table(st.session_state.history_log)
    if st.button("Clear History"):
        st.session_state.history_log = []
        st.rerun()