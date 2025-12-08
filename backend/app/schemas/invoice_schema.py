#this is the schema for genrating the invoic, like what all data the invoice(bill of rent of products) should be included
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate


#  CREATE INVOICE (user request body)
class InvoiceCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None


#  INVOICE ITEM RESPONSE (calculated), for rent of each item
class InvoiceItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    qty: int
    unit_total: float     # unit_price * qty
    days_in_inventory: int
    rent_per_day: float
    total_rent: float     # rent_per_day * days_in_inventory



#  INVOICE RESPONSE (returned to client)for calculating the total product cost
class InvoiceResponse(BaseModel):
    id: str = Field(..., alias="_id")
    cust_id: str
    customer_name :str
    customer_email : str
    items: List[InvoiceItemResponse]
    rent_before_gst: float
    gst_amount: float
    total_rent: float     # final total including gst
    pdf_url: Optional[str] = None
    created_at: datetime

    class Config:
        allow_population_by_field_name = True

# invoice_Doc, and InvoiceResponse should match
    # invoice_doc = {
    #     "cust_id": ObjectId(user_id),
    #     "customer_name": customer_name,
    #     "customer_email": customer_email,
    #     "items": invoice_items,
    #     "rent_before_gst": round(total_rent_before_gst, 2),
    #     "gst_amount": gst_amount,
    #     "total_rent": final_total_rent,
    #     "pdf_url": None,
    #     "created_at": datetime.utcnow()
    # }