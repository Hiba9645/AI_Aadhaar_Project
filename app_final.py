import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
import pytesseract
import re
import platform
from PIL import Image

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@st.cache_resource
def load_my_model():
    return tf.keras.models.load_model("fraud_model.h5")

MODEL = load_my_model()

def milestone1_preprocess(img):
    """Resizes and sharpens the image"""
    img_resized = cv2.resize(img, (800, 500))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    sharpened = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

def run_fraud_detection(img):
    """Runs the H5 model to check for tampering"""
    img_input = cv2.resize(img, (96, 96))
    img_scaled = img_input / 255.0
    img_batch = np.expand_dims(img_scaled, axis=0)
    prediction = MODEL.predict(img_batch)
    score = float(prediction[0][0])
    label = "Tampered" if score > 0.5 else "Original"
    return label, score

def run_ocr(img):
    """Checks if an Aadhaar number exists"""
    text = pytesseract.image_to_string(img)
    match = re.search(r'(\d{4}[\s.]?\d{4}[\s.]?\d{4}|\d{12})', text)
    return bool(match)

st.set_page_config(page_title="Aadhaar Fraud Shield", layout="centered")
st.title("🛡️ Aadhaar Fraud Detection System")

st.markdown("---")

uploaded_file = st.file_uploader("Upload Aadhaar Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    if st.button("Verify Document"):
        with st.spinner("Analyzing..."):
            
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            raw_img = cv2.imdecode(file_bytes, 1)

            processed_img = milestone1_preprocess(raw_img)
            fraud_label, fraud_score = run_fraud_detection(processed_img)
            has_aadhaar_number = run_ocr(processed_img)

            overall_status = "VERIFIED" if (fraud_label == "Original" and has_aadhaar_number) else "REJECTED"

            st.markdown("---")
            if fraud_label == "Tampered":
                st.error(f" AUTHENTICITY: {fraud_label}")
            else:
                st.success(f" AUTHENTICITY: {fraud_label}")
            
            if overall_status == "VERIFIED":
                st.success("🏁 FINAL VERDICT: KYC APPROVED")
                st.balloons()
            else:
                st.error("🏁 FINAL VERDICT: KYC REJECTED")