#incoice matlnb bill, this will genrate the bill and store it in the JSON format in the database, inside the Invoice collection
#this file incldues the logic, matlb the INVOICE_ROUTES, will call these functins to do CURD operations on INVOICE like genrating invoice (invoice=rent), and these fucntions will take the data from the INOVOICE_API_ROUTES, Create the INVOICE(claculate rent), store them in the database, and return a responce to the API

from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException

from app.database import products_collection, invoices_collection
from app.config import RENT_RATE, GST_RATE

from app.schemas.invoice_schema import (
    InvoiceCreate,
    InvoiceItemResponse,
    InvoiceResponse
)

#for calling the functions to get all produccsts from cust_id
from app.services.product_service import create_product, get_products, get_product, update_product, delete_product

#   RENT CALCULATION (Per Day Logic)
def calculate_rent_per_day(unit_price: float, qty: int, created_at: datetime, rent_rate=RENT_RATE):
    today = datetime.now(timezone.utc)
    # convert string to datetime if needed
    # Convert string to datetime if needed
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    # If naive datetime from DB, make it aware in UTC
    elif isinstance(created_at, datetime) and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)



    days_in_inventory = (today - created_at).days
    if days_in_inventory < 1:
        days_in_inventory = 1

    unit_total = unit_price * qty
    rent_per_day = unit_total * rent_rate
    total_rent = rent_per_day * days_in_inventory

    return {
        "days_in_inventory": days_in_inventory,
        "unit_total": round(unit_total, 2),
        "rent_per_day": round(rent_per_day, 2),
        "total_rent": round(total_rent, 2)
    }



#  CREATE INVOICE (With Per-Day Rent + GST)
async def create_invoice(cust_id: str, customer_name: str, customer_email: str):

    products = await get_products(cust_id)
    if not products:
        raise HTTPException(status_code=400, detail="No products found for this user")

    invoice_items = []
    total_rent_before_gst = 0

    for product in products:
        qty = product["quantity"]
        unit_price = product["price"]
        created_at = product["created_at"]

        if qty <= 0:
            raise HTTPException(400, "Quantity must be positive")

        rent_data = calculate_rent_per_day(
            unit_price=unit_price,
            qty=qty,
            created_at=created_at
        )

        total_rent_before_gst += rent_data["total_rent"]

        invoice_items.append({
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": unit_price,
            "qty": qty,
            "unit_total": rent_data["unit_total"],
            "days_in_inventory": rent_data["days_in_inventory"],
            "rent_per_day": rent_data["rent_per_day"],
            "total_rent": rent_data["total_rent"]
        })

    # GST calculation
    gst_amount = round(total_rent_before_gst * GST_RATE, 2)
    final_total_rent = round(total_rent_before_gst + gst_amount, 2)

    invoice_doc = {
        "cust_id": ObjectId(cust_id),
        "customer_name": customer_name,
        "customer_email": customer_email,
        "items": invoice_items,
        "rent_before_gst": round(total_rent_before_gst, 2),
        "gst_amount": gst_amount,
        "total_rent": final_total_rent,
        "pdf_url": None,
        "created_at": datetime.utcnow()
    }

    # Delete all previous invoices for this customer, so that it will make sure thta, only the latest invoice are store for that user    
    await invoices_collection.delete_many({"cust_id": ObjectId(cust_id)}) 

    res = await invoices_collection.insert_one(invoice_doc)

    saved_invoice = await invoices_collection.find_one({"_id": res.inserted_id})
    saved_invoice["_id"] = str(saved_invoice["_id"])
    saved_invoice["cust_id"] = str(saved_invoice["cust_id"])
   
    return saved_invoice