import cv2
import numpy as np
import tensorflow as tf
import pytesseract
import re
from fastapi import FastAPI, UploadFile, File
from datetime import datetime

app = FastAPI()

MODEL = tf.keras.models.load_model("fraud_model.h5")

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
        full_num = re.sub(r'\D', '', match.group(0))
        masked = f"XXXX-XXXX-{full_num[-4:]}"
        return True, masked

    return False, "Not Detected"

@app.post("/verify")
async def verify_aadhaar(file: UploadFile = File(...)):
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    raw_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if raw_img is None:
        return {"error": "Invalid Image"}

    processed_img = milestone1_preprocess(raw_img)
    fraud_label, fraud_score = run_fraud_detection(processed_img)
    has_aadhaar, masked_id = run_ocr_with_masking(processed_img)

    overall_status = "VERIFIED" if (fraud_label == "Original" and has_aadhaar) else "REJECTED"

    return {
        "fraud_result": fraud_label,
        "fraud_score": round(fraud_score, 4),
        "masked_id": masked_id,
        "final_status": overall_status,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }