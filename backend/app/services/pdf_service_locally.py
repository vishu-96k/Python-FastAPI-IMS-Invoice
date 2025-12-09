#This file (pdf_service.py) handles creating invoice PDFs and uploading them to S3.
#In short: It converts invoice data → HTML → PDF → uploads to S3 → returns the URL.
# app/services/pdf_service.py
# app/services/pdf_service.py
#this file nis of no use, becoz we will be storing the pdfs into S3 bucket, but this file stores the pdfs, into the localy file system of ur PC

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bson import ObjectId
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

from app.database import invoices_collection

# -------------------------------------------------------------
# TEMPLATE & DIRECTORY SETTINGS
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # app/
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
PDF_DIR = os.path.join(BASE_DIR, "PDFs")

# Create PDFs folder if not exists
os.makedirs(PDF_DIR, exist_ok=True)

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

_executor = ThreadPoolExecutor(max_workers=2)


# -------------------------------------------------------------
# 1) FETCH INVOICE USING cust_id
# -------------------------------------------------------------
async def get_invoice_by_customer_id(cust_id: str):
    """
    Fetch invoice document from MongoDB based on customer ID.
    """
    invoice = await invoices_collection.find_one({"cust_id": ObjectId(cust_id)})

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found for given customer ID")

    invoice["_id"] = str(invoice["_id"])
    invoice["cust_id"] = str(invoice["cust_id"])

    return invoice


# -------------------------------------------------------------
# 2) PDF RENDERER (xhtml2pdf)
# -------------------------------------------------------------
def render_pdf(html_string: str, output_path: str):
    """
    Convert HTML → PDF and save to given file path.
    """
    with open(output_path, "wb") as f:
        pisa_status = pisa.CreatePDF(html_string, dest=f)

    return not pisa_status.err  # True = success


# -------------------------------------------------------------
# 3) GENERATE PDF LOCALLY
# -------------------------------------------------------------
async def generate_invoice_pdf_local(cust_id: str) -> dict:
    """
    Steps:
    1. Find invoice by customer ID
    2. Render HTML template
    3. Convert to PDF
    4. Save to app/PDFs/
    5. Return invoice + path
    """
    invoice = await get_invoice_by_customer_id(cust_id) #invoice has all the invoice data, in JSON format

    # Render HTML using Jinja2 template
    template = env.get_template("invoice.html")
    html = template.render(invoice=invoice)

    # PDF Output Path, and file name
    pdf_filename = f"{invoice['_id']}.pdf"
    output_path = os.path.join(PDF_DIR, pdf_filename)

    # Run PDF conversion in thread
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(_executor, render_pdf, html, output_path)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    return {
        "invoice": invoice,
        "pdf_path": output_path
    }
