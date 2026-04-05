import tensorflow as tf
from tensorflow.keras import layers, models


train_data = tf.keras.preprocessing.image_dataset_from_directory(
    "dataset_final/train",
    image_size=(96, 96),
    batch_size=16
)

test_data = tf.keras.preprocessing.image_dataset_from_directory(
    "dataset_final/test",
    image_size=(96, 96),
    batch_size=16
)


train_data = train_data.map(lambda x, y: (x/255.0, y)).cache().prefetch(buffer_size=tf.data.AUTOTUNE)
test_data = test_data.map(lambda x, y: (x/255.0, y)).cache().prefetch(buffer_size=tf.data.AUTOTUNE)

model = models.Sequential([
    layers.Conv2D(16, (3,3), activation='relu', input_shape=(96,96,3)),
    layers.MaxPooling2D(),

    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(),

    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])


model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)


model.fit(train_data, epochs=3, validation_data=test_data)


model.fit(train_data, epochs=5, validation_data=test_data)


model.save("fraud_model.h5")

print(" Milestone 3 Training Completed!")