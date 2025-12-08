# app/schemas/user_schema.py
# Purpose: validate request bodies and responses.
# Example: UserCreate(name="Vish", email="a@b.com", password="secret").

# ---------------------- IMPORTS ----------------------

from pydantic import BaseModel, EmailStr, Field   
# BaseModel → Parent class for creating Pydantic schema models, for validating
# EmailStr → Validates email format automatically
# Field → Used to rename fields (example: _id → id in response)

from enum import Enum
from datetime import datetime
# datetime → Used to store and return created_at time

from typing import Optional
# Optional → Makes a field optional (not used here but useful in schemas)

from bson import ObjectId
# ObjectId → MongoDB's special ID type (we convert this to string when returning JSON)

class UserType(str, Enum):  #for the chossing as the type
    admin = "admin"
    user = "user"


# =====================================================
#  SCHEMA FOR SIGNUP REQUEST (Data coming from frontend)
# =====================================================
class UserCreate(BaseModel):
    name: str                 # User's full name (required)
    email: EmailStr           # Valid email required, auto-validated
    phone: str                # Phone number, must be a number
    password: str             # Password in plain text (will be hashed later)
    type : UserType              # User type: "admin" or "user"


# =====================================================
#  SCHEMA FOR LOGIN REQUEST (Data coming from frontend)
# =====================================================
class UserLogin(BaseModel):
    email: EmailStr           # Login email → must be valid
    password: str             # Login password (plain text, to check hash)


# =====================================================
#  SCHEMA FOR RESPONSE (What API returns to frontend)
# =====================================================
class UserResponse(BaseModel):
    
    id: str = Field(..., alias="_id")  
    # MongoDB returns "_id"
    # But frontend should receive "id"
    # Field(alias="_id") → rename _id → id in response

    name: str                 # User's name to return to frontend
    email: EmailStr           # User's email to return
    created_at: datetime      # User's account creation time


    class Config:
        allow_population_by_field_name = True
        # Allows you to create this model with either:
        # id="123" OR _id="123"
        # Both will work.

        json_encoders = {ObjectId: str}
        # Converts MongoDB ObjectId → string
        # Because frontend cannot read ObjectId

# --------------------------------------------------
# Pydantic models are NOT database models — they are data validation + request/response format models.
"""
✅ Why do we need this file?
1️⃣ To validate incoming data
Example: When someone signs up, the API must check: name is string and etc

2️⃣ To define how data should look in API requests
UserCreate → defines the shape of data you must send during signup
(Example: name, email, phone, password, type)


✅Does user_schema store data in the database?
👉 NO.
Schemas NEVER store data.
MongoDB stores data.
Schemas only validate + structure the data before inserting.

we are using this file, only for data validation, like email validation, creating user classs objects which will store the diff feilds and can pass the data to the database
    

✅ What exactly are we doing with user_schema?
1️⃣ Validating input : when someone sends data from the API, then email validate, password validate etc

2️⃣ Structuring input/output
UserCreate → structure of data you receive from frontend
UserResponse → structure of data you return to frontend

3️⃣ Converting MongoDB data to JSON   

❓ Can we make routes WITHOUT using user_schema?
👉 YES, you can, but it is a bad practice.


❓ Why don't we use user_model instead?

Because:MongoDB does NOT need models, It is schema-less, so we are only doing data validations.


🟩 So final answer in 4 lines (very simple):
user_schema validates data and controls API input/output.
Routes can work without it, but validation becomes poor → bad API.
user_model is not used because MongoDB doesn’t need models.
Best practice: MongoDB + FastAPI = Pydantic schemas for request/response. """



# thats it tell me step by step approach to do this, and what all files should be there, like I have 
