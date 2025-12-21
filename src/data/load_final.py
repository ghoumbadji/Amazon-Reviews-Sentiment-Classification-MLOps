"""
Upload cleaned data into S3.
"""

import os
import boto3


def load_to_s3_final(bucket_name, local_file, output_key):
    """Load cleaned data to S3."""
    s3 = boto3.client("s3")
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"File {local_file} does not exist.")
    print(f"Uploading cleaned file to {bucket_name}/{output_key}...")
    s3.upload_file(local_file, bucket_name, output_key)
    print("Data pipeline finished successfully.")
