"""Put all of the data pipeline steps together."""

import os
import sys
from botocore.exceptions import BotoCoreError, ClientError
import download_data
import clean_transform
import load_final


# Configuration
BUCKET_NAME = os.getenv("BUCKET_NAME")
RAW_S3_KEY = "data/raw/amazon_polarity.parquet"
RAW_LOCAL_FILE = "temp_raw.parquet"
CLEAN_LOCAL_FILE = "temp_clean.parquet"
PROCESSED_S3_KEY = "data/processed/amazon_polarity_cleaned.parquet"


def run_data_pipeline():
    """Full data pipeline"""
    print("Starting Automated Data Pipeline")
    # Step 1: Ingest
    print("Step 1: Data Ingestion")
    try:
        download_data.download_and_upload_raw(
            bucket_name=BUCKET_NAME,
            s3_key=RAW_S3_KEY,
            local_file=RAW_LOCAL_FILE
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Pipeline failed at Step 1 (Download): {e}")
        sys.exit(1)
    print("\n-----------------------------------------\n")
    # Step 2: Transform
    print("Step 2: Data Transformation")
    try:
        clean_transform.process_data(
            bucket_name=BUCKET_NAME,
            input_key=RAW_S3_KEY,
            local_input=RAW_LOCAL_FILE,
            local_output=CLEAN_LOCAL_FILE
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Pipeline failed at Step 2 (Transform): {e}")
        sys.exit(1)
    print("\n-----------------------------------------\n")
    # Step 3: Load
    print("Step 3: Data Loading")
    try:
        load_final.load_to_s3_final(
            bucket_name=BUCKET_NAME,
            local_file=CLEAN_LOCAL_FILE,
            output_key=PROCESSED_S3_KEY
        )
    except (FileNotFoundError, BotoCoreError, ClientError) as e:
        print(f"Pipeline failed at Step 3 (Load): {e}")
        sys.exit(1)
    print("\nPipeline completed successfully.")
