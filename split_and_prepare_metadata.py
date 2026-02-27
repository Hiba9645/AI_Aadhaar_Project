import os
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split


df = pd.read_csv("dataset/labels.csv")


train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["label"] 
)

base_output = "dataset_final"

folders = [
    "train/original",
    "train/tampered",
    "test/original",
    "test/tampered"
]

for folder in folders:
    os.makedirs(os.path.join(base_output, folder), exist_ok=True)


def copy_images(dataframe, subset):
    for _, row in dataframe.iterrows():
        filename = row["filename"]
        label = row["label"]

        source_path = os.path.join("dataset_preprocessed", label, filename)
        dest_path = os.path.join(base_output, subset, label, filename)

        if os.path.exists(source_path):
            shutil.copy(source_path, dest_path)


copy_images(train_df, "train")
copy_images(test_df, "test")


train_df.to_csv(os.path.join(base_output, "train_metadata.csv"), index=False)
test_df.to_csv(os.path.join(base_output, "test_metadata.csv"), index=False)

print("Train-Test split and metadata extraction completed successfully")