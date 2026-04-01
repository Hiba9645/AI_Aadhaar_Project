import tensorflow as tf
import cv2
import numpy as np
import os

model = tf.keras.models.load_model("fraud_model.h5")

folder = "test_images"  

for file in os.listdir(folder):
    path = os.path.join(folder, file)

    img = cv2.imread(path)
    if img is None:
        continue

    img = cv2.resize(img, (96, 96))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)

    if prediction[0][0] > 0.5:
        result = "Tampered "
    else:
        result = "Original "

    print(f"{file} → {result}")