from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    quantity: int

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    quantity: Optional[int]

class ProductResponse(BaseModel):
    id: str = Field(..., alias="_id")
    owner_id: str
    name: str
    description: Optional[str]
    price: float
    quantity: int
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
"""
This file will contain classes (schemas) that act like blueprints for a product.
These schemas help us send product data to the database in a clean and structured way.

These classes are used for data validation only.
When you create or update a product, the schema checks the fields (name, price, quantity, etc.) and creates a product object that is safe to store in the database.

So basically:
Schemas = rules + shape of product data
They make sure only correct data goes in/out of the database.
"""