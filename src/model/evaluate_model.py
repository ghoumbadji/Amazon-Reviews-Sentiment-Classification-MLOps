"""
Evaluate the LSTM model.
"""

import os
import json
import pickle
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from src.utils.s3_utils import download_file_from_s3, upload_file_to_s3


# Configuration
BUCKET_NAME = os.getenv("BUCKET_NAME")
DATA_KEY = "data/processed/amazon_polarity_cleaned.parquet"
LOCAL_DATA_FILE = "amazon_polarity_cleaned.parquet"

# S3 keys to fetch
MODEL_S3_KEY = "models/sentiment_model.keras"
TOKENIZER_S3_KEY = "models/tokenizer.pickle"

# S3 keys (Outputs)
METRICS_S3_KEY = "models/evaluation_results.json"


def get_test_data():
    """
    Downloads data and recreates the split to isolate the Test set.
    We use the exact same random_state as in the training script.
    """
    if not os.path.exists(LOCAL_DATA_FILE):
        download_file_from_s3(BUCKET_NAME, DATA_KEY, LOCAL_DATA_FILE)
    df = pd.read_parquet(LOCAL_DATA_FILE)
    # Recreate the split
    _, X_test, _, y_test = train_test_split(
        df["content"], df["label"], test_size=0.2, stratify=df["label"], random_state=42
    )
    return X_test, y_test


def load_artifacts():
    """Download and load artifacts"""
    # 1. Download artifacts
    local_model = "downloaded_model.keras"
    local_tokenizer = "downloaded_tokenizer.pickle"
    download_file_from_s3(BUCKET_NAME, MODEL_S3_KEY, local_model)
    download_file_from_s3(BUCKET_NAME, TOKENIZER_S3_KEY, local_tokenizer)
    # 2. Load artifacts
    model = tf.keras.models.load_model(local_model)
    with open(local_tokenizer, "rb") as handle:
        tokenizer = pickle.load(handle)
    return model, tokenizer


def prepare_test_data(tokenizer):
    """Prepare test data for evaluation."""
    x_test_raw, y_test = get_test_data()
    x_test_seq = tokenizer.texts_to_sequences(x_test_raw)
    x_test_pad = keras.utils.pad_sequences(
        x_test_seq, padding="post", maxlen=128
    )
    return x_test_pad, y_test


def evaluate_model(model, x_test_pad, y_test):
    """Evaluate the model and output metrics."""
    results = model.evaluate(x_test_pad, y_test, verbose=0)
    y_pred_prob = model.predict(x_test_pad)
    y_pred = (y_pred_prob > 0.5).astype(int)
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    return results, report_dict


def save_and_upload_metrics(results, report_dict):
    """Upload evaluation metrics into S3."""
    metrics_data = {
        "global_score": {
            "loss": float(results[0]),
            "accuracy": float(results[1]),
            "precision": float(results[2]),
            "recall": float(results[3]),
        },
        "classification_report": report_dict,
    }
    local_metrics_file = "metrics.json"
    with open(local_metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
    upload_file_to_s3(local_metrics_file, BUCKET_NAME, METRICS_S3_KEY)


def main():
    """Main function"""
    print("Starting evaluation process...")
    # 1. Download and load artifacts
    model, tokenizer = load_artifacts()
    # 2. Prepare test data
    x_test_pad, y_test = prepare_test_data(tokenizer)
    # 3. Compute metrics
    print("Calculating metrics...")
    results, report_dict = evaluate_model(model, x_test_pad, y_test)
    # 4. Save metrics
    save_and_upload_metrics(results, report_dict)
    print("Evaluation complete and metrics uploaded.")
