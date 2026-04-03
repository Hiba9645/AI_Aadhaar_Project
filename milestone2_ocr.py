import os
import cv2
import pytesseract
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor
from PIL import Image


#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


folders = {
    "original": "dataset_final/train/original",
    "tampered": "dataset_final/train/tampered"
}


def extract_text(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
       
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        text = pytesseract.image_to_string(thresh, lang='eng')
        return text
    except:
        return ""

def extract_fields(ocr_text):
    fields = {"Name": "", "DOB": "", "Aadhaar": ""}

    
    name_match = re.search(r'Name[: ]+([A-Za-z ]+)', ocr_text)
    if name_match:
        fields["Name"] = name_match.group(1).strip()

   
    dob_match = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4}/\d{4}|\d{6,8})', ocr_text)
    if dob_match:
        dob_raw = dob_match.group(1)
        
        dob_digits = re.sub(r'\D', '', dob_raw)
        if len(dob_digits) == 8:
            fields["DOB"] = f"{dob_digits[:2]}/{dob_digits[2:4]}/{dob_digits[4:]}"
        elif len(dob_digits) == 6:  
            fields["DOB"] = f"{dob_digits[:2]}/01/{dob_digits[2:]}"  
        else:
            fields["DOB"] = dob_raw
   
    aadhaar_match = re.search(r'(\d{4}\s?\d{4}\s?\d{4}|\d{12})', ocr_text)
    if aadhaar_match:
        aadhaar_digits = re.sub(r'\D', '', aadhaar_match.group(1))
        if len(aadhaar_digits) == 12:
            fields["Aadhaar"] = f"{aadhaar_digits[:4]} {aadhaar_digits[4:8]} {aadhaar_digits[8:]}"
    return fields


def validate_fields(fields):
    result = {}
    result["Name_Valid"] = bool(fields["Name"]) and all(c.isalpha() or c.isspace() for c in fields["Name"])
    result["DOB_Valid"] = bool(re.match(r'^\d{2}/\d{2}/\d{4}$', fields["DOB"]))
    result["Aadhaar_Valid"] = bool(re.match(r'^\d{4}\s\d{4}\s\d{4}$', fields["Aadhaar"]))
    result["Document_Valid"] = result["Name_Valid"] and result["DOB_Valid"] and result["Aadhaar_Valid"]
    return result


def process_image(args):
    label, file_path = args
    ocr_text = extract_text(file_path)
    fields = extract_fields(ocr_text)
    validation = validate_fields(fields)
    data = {
        "File": os.path.basename(file_path),
        "Label": label,
        "Name": fields["Name"],
        "DOB": fields["DOB"],
        "Aadhaar": fields["Aadhaar"],
        "Name_Valid": validation["Name_Valid"],
        "DOB_Valid": validation["DOB_Valid"],
        "Aadhaar_Valid": validation["Aadhaar_Valid"],
        "Document_Valid": validation["Document_Valid"]
    }
    return data


all_files = []
for label, folder in folders.items():
    for file in os.listdir(folder):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            all_files.append((label, os.path.join(folder, file)))

all_data = []
with ThreadPoolExecutor(max_workers=8) as executor:
    results = executor.map(process_image, all_files)
    all_data.extend(results)


df = pd.DataFrame(all_data)
df.to_csv("milestone2_output.csv", index=False)
print("Milestone 2 complete! CSV saved as milestone2_output.csv")