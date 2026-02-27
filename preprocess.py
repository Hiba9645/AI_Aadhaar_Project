import cv2
import os

folders = ["dataset/original", "dataset/tampered"]

for folder in folders:
    out_folder = folder.replace("dataset", "dataset_preprocessed")
    os.makedirs(out_folder, exist_ok=True)
    
    for img_file in os.listdir(folder):
        path = os.path.join(folder, img_file)
        img = cv2.imread(path)
        
        if img is None:
            continue
        
        img = cv2.resize(img, (800, 500))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3,3), 0)
        cv2.imwrite(os.path.join(out_folder, img_file), gray)

print("All images preprocessed successfully")