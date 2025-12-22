"""
Build and train a binary classification model using BiLSTMs.
"""

import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from src.utils.s3_utils import download_file_from_s3, upload_file_to_s3

# Configuration
BUCKET_NAME = os.getenv("BUCKET_NAME")
DATA_KEY = "data/processed/amazon_polarity_cleaned.parquet"
LOCAL_DATA_FILE = "amazon_polarity_cleaned.parquet"

# Artifact paths in S3
MODEL_S3_KEY = "models/sentiment_model.keras"
TOKENIZER_S3_KEY = "models/tokenizer.pickle"


def load_and_split_data():
    """Downloads data and splits it. Returns training data."""
    if not os.path.exists(LOCAL_DATA_FILE):
        download_file_from_s3(BUCKET_NAME, DATA_KEY, LOCAL_DATA_FILE)
    df = pd.read_parquet(LOCAL_DATA_FILE)
    X = df["content"]
    y = df["label"]
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)


def create_lstm_model(vocab_size):
    """Defines the LSTM architecture."""
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, 32),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True)),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(16)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])
    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(1e-3),
        metrics=["accuracy", "precision", "recall"]
    )
    return model


def main():
    """Main function."""
    # 1. Data Splitting
    print("Preparing data...")
    X_train, _, y_train, _ = load_and_split_data()
    # 2. Tokenization
    max_vocab = 10000
    tokenizer = keras.preprocessing.text.Tokenizer(num_words=max_vocab)
    tokenizer.fit_on_texts(X_train) # Fit only on training data
    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_train_pad = keras.utils.pad_sequences(X_train_seq, padding="post", maxlen=128)
    # 3. Model Training
    print("Starting training...")
    model = create_lstm_model(max_vocab)
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=2, restore_best_weights=True
    )
    model.fit(
        X_train_pad, y_train,
        epochs=20,
        validation_split=0.1,
        batch_size=32,
        callbacks=[early_stop]
    )
    # 4. Save Artifacts and Upload to S3
    print("Saving artifacts...")
    # Save & Upload Model
    local_model_path = "model_temp.keras"
    model.save(local_model_path)
    upload_file_to_s3(local_model_path, BUCKET_NAME, MODEL_S3_KEY)
    # Save & Upload Tokenizer
    local_tok_path = "tokenizer_temp.pickle"
    with open(local_tok_path, "wb") as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    upload_file_to_s3(local_tok_path, BUCKET_NAME, TOKENIZER_S3_KEY)
    print("Training finished and artifacts uploaded to S3.")
