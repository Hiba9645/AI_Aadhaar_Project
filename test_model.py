import tensorflow as tf
import cv2
import numpy as np


model = tf.keras.models.load_model("fraud_model.h5")


img = cv2.imread("img_38.png")  
img = cv2.resize(img, (96, 96))
img = img / 255.0
img = np.expand_dims(img, axis=0)


prediction = model.predict(img)

if prediction[0][0] > 0.5:
    print(" Tampered Document")
else:
    print(" Original Document")