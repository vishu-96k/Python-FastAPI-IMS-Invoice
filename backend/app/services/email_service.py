#this file incldues the logic, matlb the PRODUCTS_ROUTES, will call these functins to do CURD operations on producs, and these fucntions will take the data from the RPODUCT_API_ROUTES, Create the producst, store them in the database, and return a responce to the API

# app/services/email_service.py
# app/services/email_service.py
import os
import aiosmtplib
from email.message import EmailMessage
from decouple import config    
from app.services.pdf_service_locally import generate_invoice_pdf_local, get_invoice_by_customer_id

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # app/
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
PDF_DIR = os.path.join(BASE_DIR, "PDFs")


SMTP_HOST = config("SMTP_HOST")
SMTP_PORT = int(config("SMTP_PORT", 587))
SMTP_USER = config("SMTP_USER")
SMTP_PASS = config("SMTP_PASS")
EMAIL_FROM = config("EMAIL_FROM", "noreply@example.com")


async def send_email_with_attachment(
    cust_id : str,
    cust_name : str,
    cust_email: str,
    cust_phone: str,
):
    
    invoice =  await get_invoice_by_customer_id(cust_id)
    pdf_path = os.path.join(PDF_DIR, f"{invoice['_id']}.pdf")
    subject="Your Invoice"
    S3_url = str(invoice["pdf_url"])

    #Read PDF file bytes
    with open(pdf_path, "rb") as f:
        attachment_bytes = f.read()
    filename = os.path.basename(pdf_path)

    body = (
        f"Hello {cust_name},\n\n"
        f"Your invoice is attached.\n\n"
        f"CUSTOMER ID: {cust_id}\n"
        f"CUSTOMER PHONE: {cust_phone}\n"
        f"DOWNLOAD: {S3_url}\n"
    )


    # Create email message
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = cust_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach PDF
    msg.add_attachment(
        attachment_bytes,
        maintype="application",
        subtype="pdf",
        filename=filename
    )

    # Send email
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True
    )

    return {"status": "Email sent"}
