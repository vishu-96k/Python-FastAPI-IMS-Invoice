#this file will upload the genrated PDF, to the s3 Bucket
#storage_service.py handles uploading PDF files to AWS S3 and then deleting the PDF from local storage.
# It is the storage layer of your backend, responsible only for file handling — NOT PDF creation, only uploading + cleanup.

# app/services/storage_service.py
import os
import aioboto3
from botocore.config import Config
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient   # Import async MongoDB client (Motor driver)
from decouple import config      


AWS_REGION =  config("AWS_REGION")
AWS_ACCESS_KEY =  config("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY =  config("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = config("S3_BUCKET")
# S3_BUCKET = os.getenv("S3_BUCKET") this os.getenv will not work, so use Config() fun to get the env variables  

# Create aioboto3 session
session = aioboto3.Session()

# Path: app/services → so BASE_DIR = app/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# PDF folder: app/PDFs
PDF_DIR = os.path.join(BASE_DIR, "PDFs")


async def upload_pdf_to_s3(pdf_filename: str):
    """
    Uploads a locally stored PDF from app/PDFs/ to S3 bucket.
    After upload → deletes the local file.
    """
    print("DEBUG S3_BUCKET =", S3_BUCKET)
    # Full local file path
    local_pdf_path = os.path.join(PDF_DIR, pdf_filename)

    if not os.path.exists(local_pdf_path):
        raise FileNotFoundError(f"PDF not found: {local_pdf_path}")

    async with session.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        config=Config(signature_version="s3v4")
    ) as s3:

        # S3 key (folder inside bucket)  
        s3_key = f"invoices/{pdf_filename}"

        # Upload file
        await s3.upload_file(local_pdf_path, S3_BUCKET, s3_key)

        # S3 public URL (if bucket is public)
        s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

# -------- DELETE ALL PREVIOUS LOCAL FILES EXCEPT CURRENT ---------
        try:
            for file in os.listdir(PDF_DIR):
                file_path = os.path.join(PDF_DIR, file)

                # Skip folders
                if os.path.isdir(file_path):
                    continue

                # Skip the newly created file
                if file == pdf_filename:
                    continue

                # Delete old file
                os.remove(file_path)
                print(f"Deleted old PDF: {file_path}")

        except Exception as e:
            print("Failed to clean PDFs folder:", e)

        return s3_url


'''
 --------------EXPLANATION -----------
The storage_service.py file is responsible only for handling the uploading of invoice PDF files to AWS S3. It does not generate PDFs; instead, it receives the name of a PDF file that already exists locally inside the app/PDFs/ folder. Using this filename, the service builds the full file path and prepares the file for upload.

Once the file is located, the service creates an asynchronous S3 client using aioboto3 and uploads the PDF to the specified S3 bucket under a folder named invoices/. After a successful upload, it generates the public S3 URL for the uploaded PDF, allowing other parts of the system — or the frontend — to access or download it.

Finally, to save storage space and avoid unnecessary file accumulation on the server, the service deletes the local copy of the PDF after uploading it to S3. In simple terms, this file takes a local PDF, uploads it to cloud storage, returns the cloud URL, and removes the local version to keep the backend clean.

Flow Summary (very clear)
pdf_service.py  
    ↓
Creates PDF inside → app/PDFs/invoice_xxx.pdf  
    ↓
invoice_router  
    ↓
Calls storage_service.upload_pdf_to_s3(pdf_filename)  
    ↓
storage_service.py  
    ↓
Uploads to S3  
Deletes local file  
Returns final S3 URL  

'''

