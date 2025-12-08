#this file incldues the logic, matlb the PRODUCTS_ROUTES, will call these functins to do CURD operations on producs, and these fucntions will take the data from the RPODUCT_API_ROUTES, Create the producst, store them in the database, and return a responce to the API

# app/services/email_service.py
import os
import aiosmtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@example.com")

async def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_bytes: bytes, filename: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    msg.add_attachment(attachment_bytes, maintype="application", subtype="pdf", filename=filename)

    await aiosmtplib.send(msg,
                         hostname=SMTP_HOST,
                         port=SMTP_PORT,
                         username=SMTP_USER,
                         password=SMTP_PASS,
                         start_tls=True)
