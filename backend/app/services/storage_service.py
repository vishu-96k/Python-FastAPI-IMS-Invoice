#this file, It handles file upload, secure download URLs, and object retrieval from AWS S3 in an async-safe way.

# app/services/storage_service.py
import os
import aioboto3
from botocore.config import Config
from typing import Optional

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_BASE_URL = os.getenv("S3_BASE_URL")  # optional if public

_s3_kwargs = {
    "region_name": AWS_REGION,
    "aws_access_key_id": AWS_ACCESS_KEY,
    "aws_secret_access_key": AWS_SECRET_KEY,
    "config": Config(signature_version="s3v4")
}

async def upload_file(local_path: str, s3_key: str, content_type: str = "application/pdf") -> str:
    """
    Uploads local file to S3 and returns a public URL or constructed URL.
    """
    session = aioboto3.Session()
    async with session.client("s3", **_s3_kwargs) as s3:
        await s3.upload_file(Filename=local_path, Bucket=S3_BUCKET, Key=s3_key,
                             ExtraArgs={"ContentType": content_type, "ACL": "private"})
    # Return either a constructed public URL or object path. We store both key and url.
    if S3_BASE_URL:
        return S3_BASE_URL.rstrip("/") + "/" + s3_key
    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

async def generate_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    session = aioboto3.Session()
    async with session.client("s3", **_s3_kwargs) as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key},
            ExpiresIn=expires_in,
        )
    return url

async def get_object_bytes(s3_key: str) -> bytes:
    session = aioboto3.Session()
    async with session.client("s3", **_s3_kwargs) as s3:
        resp = await s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        async with resp["Body"] as stream:
            data = await stream.read()
    return data

'''
 --------------EXPLANATION -----------
This file (storage_service.py) provides all S3-related operations for your FastAPI backend using aioboto3 (async AWS SDK). It loads AWS credentials from environment variables and sets up a reusable S3 client configuration.
    
It exposes three async functions:
upload_file() → Uploads a local file to an S3 bucket with a given key, sets proper content-type, keeps the file private, and returns a public-accessible URL (either via custom base URL or default S3 URL).

generate_presigned_url() → Creates a temporary, signed URL allowing secure download of a private S3 object (default expiry 1 hour).

get_object_bytes() → Downloads a file from S3 and returns its raw bytes, useful for in-memory operations (e.g., returning PDF bytes to API).
'''
