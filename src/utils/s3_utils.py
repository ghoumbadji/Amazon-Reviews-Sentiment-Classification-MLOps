"""
Some S3 utility functions (upload and download).
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def get_s3_client():
    """Initializes the S3 client."""
    return boto3.client("s3")


def download_file_from_s3(bucket, s3_key, local_path):
    """Downloads a file from S3 to the local file system."""
    s3 = get_s3_client()
    try:
        print(f"Downloading s3://{bucket}/{s3_key} to {local_path}...")
        s3.download_file(bucket, s3_key, local_path)
        print("Download successful.")
    except (BotoCoreError, ClientError) as e:
        print(f"Error during download: {e}")
        raise


def upload_file_to_s3(local_path, bucket, s3_key):
    """Uploads a local file to S3."""
    s3 = get_s3_client()
    try:
        print(f"Uploading {local_path} to s3://{bucket}/{s3_key}...")
        s3.upload_file(local_path, bucket, s3_key)
        print("Upload successful.")
    except (BotoCoreError, ClientError) as e:
        print(f"Error during upload: {e}")
        raise
