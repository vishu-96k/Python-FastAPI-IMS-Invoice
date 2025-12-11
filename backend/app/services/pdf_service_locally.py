#This file (pdf_service.py) handles creating invoice PDFs and uploading them to S3.
#In short: It converts invoice data → HTML → PDF → uploads to S3 → returns the URL.
# app/services/pdf_service.py
# app/services/pdf_service.py
#this file nis of no use, becoz we will be storing the pdfs into S3 bucket, but this file stores the pdfs, into the localy file system of ur PC

import os                       # For file paths, folder creation, saving PDFs
import asyncio                  # To run blocking PDF code in separate threads
from concurrent.futures import ThreadPoolExecutor  # Thread pool for non-async work
from bson import ObjectId       # Convert string IDs → MongoDB ObjectId
from fastapi import HTTPException  # Raise proper HTTP errors
from jinja2 import Environment, FileSystemLoader, select_autoescape  # HTML templating
from xhtml2pdf import pisa      # Library to convert HTML → PDF
from app.database import invoices_collection  # MongoDB collection: invoices


# -------------------------------------------------------------
# TEMPLATE & DIRECTORY SETTINGS
# -------------------------------------------------------------

# BASE_DIR = app/
# __file__ = app/services/pdf_service.py → go 2 levels up
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # app/

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates") # Path to templates folder (app/templates)

PDF_DIR = os.path.join(BASE_DIR, "PDFs") # Path where generated PDFs will be saved (app/PDFs)

# Create PDFs folder if not exists
os.makedirs(PDF_DIR, exist_ok=True)


# Setup Jinja2 to load HTML templates from TEMPLATES_DIR
# autoescape → protects against HTML injection
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)


# Thread pool used to run heavy blocking tasks (PDF generation)
# max_workers=2 → Only 2 PDFs generated at once
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
        pisa_status = pisa.CreatePDF(html_string, dest=f)  # pisa.CreatePDF converts HTML into PDF content

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
    template = env.get_template("invoice.html") # Step 2 — Load invoice.html template
    html = template.render(invoice=invoice)  # Step 3 — Render template → HTML string by injecting invoice data

    # PDF Output Path, and file name
    pdf_filename = f"{invoice['_id']}.pdf"   # Step 4 — Define PDF filename with invoice ID (always unique)
    output_path = os.path.join(PDF_DIR, pdf_filename)  # app/PDFs/12345.pdf

    # Run PDF conversion in thread BECOZ Run blocking render_pdf() in a worker thread
    # Otherwise FastAPI event loop would freeze
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(_executor, render_pdf, html, output_path)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    return {
        "invoice": invoice,
        "pdf_path": output_path
    }
