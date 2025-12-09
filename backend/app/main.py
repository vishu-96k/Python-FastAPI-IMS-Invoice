#JWT, User_Schema, Env, database insab ke liye ke liye
from fastapi import FastAPI, HTTPException, status, Depends
from datetime import datetime
from bson.objectid import ObjectId
from app.database import users_collection # Database collection for users
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse # Pydantic schemas for request validation and response
from app.utils.hashing import hash_password, verify_password # Utilities for password hashing and verification
from app.utils.jwt_handler import create_access_token # JWT creation function
from app.utils.auth import get_current_user, get_optional_user # Dependency to get current logged-in user


# PRODUCTS KE LIYE 
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate
from app.utils.auth import get_current_user
from app.services.product_service import create_product, get_products, get_product, update_product, delete_product


# INVOICE (rent calculation) KE LIYE 
from app.schemas.invoice_schema import InvoiceCreate, InvoiceItemResponse, InvoiceResponse
from app.services.invoice_service import create_invoice, calculate_rent_per_day

# INVOICE PDF GENRATION KE LIYE and S3 UPLOADATION
import os
import io
from app.services import storage_service, email_service
from app.services.pdf_service_locally import generate_invoice_pdf_local, get_invoice_by_customer_id
from app.services.storage_service import upload_pdf_to_s3
from app.database import products_collection, invoices_collection

# INVOICE PDF SENDING MAIL KE LIYE
from app.services.email_service import send_email_with_attachment


app = FastAPI()  # Create FastAPI instance

#-----------------USER ROUTES--------------------
#home route
@app.get("/")
async def home(current_user=Depends(get_optional_user)): #this depends is an middle were, which will return what the funtion uh have sended in it
    if current_user:
        return {"msg": f"Hello {current_user['name']}, you are logged in!"}
    else:
        return {"msg": "Welcome Guest! Please login or signup."}

#this route, creaets a user, and store it in data base, and returns the user_id
@app.post("/auth/signup", response_model=UserResponse)
async def signup(user: UserCreate):

    existing = await users_collection.find_one({"email": user.email}) # Check if email already exists in database
    if existing:
        raise HTTPException(400, "Email already registered")

    user_dict = user.dict()     # Convert user Pydantic object to dict


    user_dict["password"] = hash_password(user_dict["password"][:72])     # Hash the password before storing, and truncate the passwor if its long

    user_dict["created_at"] = datetime.utcnow()     # Add creation timestamp

    result = await users_collection.insert_one(user_dict)     # Insert the user into MongoDB

    new_user = await users_collection.find_one({"_id": result.inserted_id})     # Retrieve the newly created user from DB

    new_user["_id"] = str(new_user["_id"])     # Convert MongoDB ObjectId to string for frontend

    new_user.pop("password")     # Remove password from response

    return new_user     # Return user data to frontend

#this route takes the user id password, verifeiss it and then return a JWT token for further user
@app.post("/auth/login")
async def login(payload: UserLogin):
    
    user = await users_collection.find_one({"email": payload.email})     # Check if user exists by email
    if not user:
        raise HTTPException(401, "Invalid email or password")
    
    if not verify_password(payload.password, user["password"]):    # Verify the hashed password matches
        raise HTTPException(401, "Invalid email or password")

    user_id = str(user["_id"])    # Convert ObjectId to string for token

    access_token = create_access_token(user_id)     # Generate JWT token (signed with secret and algorithm)

    return {  # Return token to frontend
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user

#-----------------USER ROUTES--ENDED------------------

#-----------------PRODUCTS ROUTES--------------------
#FOR CREATING PRODUCTS
#For creatning products, the middlewere (depends) is also passed to check wether the user is logedin or not, and even JWT validates it
@app.post("/CreateProducts/", response_model=ProductResponse, status_code=201)
async def create_product_route(product: ProductCreate, current_user = Depends(get_current_user)): #dependecny is noth but the middlewere
    # current_user assumed like {"_id": "....", "name": "...", "email": "..."}
    owner_id = str(current_user["_id"])
    new_prod = await create_product(owner_id, product.dict())
    return new_prod

#FOR GETTING ALL PRODUCTS
@app.get("/AllProducts/", response_model= list[ProductResponse])
async def Get_products_route(current_user = Depends(get_current_user)):
    owner_id = str(current_user["_id"])
    all_products = await get_products(owner_id, skip=0)
    return all_products

#FOR GETTING SINGLE PRODUCT
@app.get("/product/{product_id}", response_model= ProductResponse)
async def Get_single_product_route(product_id: str,current_user = Depends(get_current_user)):
    owner_id = str(current_user["_id"])
    product = await get_product(owner_id, product_id)
    return product

#FOR UPDATING A PRODUCT
@app.patch("/UpdateProduct/{product_id}", response_model=ProductResponse) #response_model in FastAPI controls what the API returns to the client, and how it should look.
async def update_product_route(
    product_id: str,
    updates: ProductUpdate,
    current_user = Depends(get_current_user)
    ):
    owner_id = str(current_user["_id"])

    updated = await update_product(owner_id, product_id, updates.dict())
    return updated

#FOR DELEATING A PRODUCT
@app.delete("/DeleteProducts/{product_id}") 
async def delete_product_route(
    product_id: str,
    current_user = Depends(get_current_user)
    ):
    owner_id = str(current_user["_id"])
    deleted_product = await delete_product(owner_id, product_id)
    if(deleted_product) :
        return {
    "message": "Product deleted successfully",
    "deleted_product": deleted_product.name
}
    else :
        return "product not deleted"
    
#-----------------PRODUCTS ROUTES--ENDED-----------------

#-----------------INVOICE ROUTES--------------------
#FOR CREATING INVOICE 
@app.post("/invoice/generate", response_model=InvoiceResponse) #this will genrate invoice and store it in DB in json format
async def gen_invoice_route(current_user=Depends(get_current_user)): #thir products data is noth but the all products_id as list
    invoice = await create_invoice(
        cust_id=str(current_user["_id"]),
        customer_name=str(current_user["name"]),
        customer_email=str(current_user["email"]),
    )
    # convert _id to str in service or here
    invoice["_id"] = str(invoice["_id"])
    return invoice

#-----------------INVOICE ROUTES--ENDED-----------------

#-----------------INVOICE PDF ROUTES--------------------
@app.get("/invoice/get_pdf") #this will take the user_id from the current user, and pass it as cust_it, and find that invoice, and fetch the details, and create and genrate PDF, and even upload that pdf to S3 bucket
async def gen_invoice_pdf_route(current_user=Depends(get_current_user)):
    cust_id=str(current_user["_id"])

    # Generate invoice + local PDF file
    result = await generate_invoice_pdf_local(cust_id) #this genrates PDF locally and stores in PDFs folder

    invoice = result["invoice"] #this has the actual invoice data, becoz result has invoice, and pdf path, which is store locally
    pdf_path = result["pdf_path"]      # this is local PDF path like /tmp/invoice_123.pdf  # e.g. app/PDFs/invoice_6732ab1d.pdf

    # Extract only the filename from the path
    pdf_filename = os.path.basename(pdf_path)   # ➜ invoice_6732ab1d.pdf

    # Upload to S3
    s3_url = await upload_pdf_to_s3(pdf_filename)

    #updating the invoice, adding its S3 URL in exsisting invoices pdf_url feild
    result = await invoices_collection.update_one(
        {"cust_id": ObjectId(cust_id)},  #find the invoice based on its Cust_id, and then update pdf_url feild 
        {"$set": {"pdf_url": s3_url}} #set the s3 url as PDF URL in the invoice collection 
    )

    return {
        "message": "PDF generated & uploaded successfully",
        "invoice": invoice,
        "local_pdf_path": pdf_path,
        "s3_url": s3_url
    }
#-----------------INVOICE PDF ROUTES--ENDED-----------------

#-----------------INVOICE EMAIL ROUTES--------------------
@app.post("/invoice/send-invoice-mail")
async def send_invoice_mail_route(current_user=Depends(get_current_user)):
    cust_id=str(current_user["_id"])
    cust_name=str(current_user["name"])
    cust_email=str(current_user["email"])
    cust_phone = str(current_user["phone"])
    print(cust_email)

    await send_email_with_attachment(
        cust_id,
        cust_name,
        cust_email,
        cust_phone,
    )
    return {"message": "Invoice emailed successfully"}











































#-----------------ADMIN ROUTES-------------------
#only for admin routes
# @app.get("/admin/AllInnvoice") #only for admin, admin can see all the invoice form the database genrater sp for
# async def admin_products_route(current_user = Depends(get_current_user)):
#     owner_id = str(current_user["_id"])
#     # TYPE = str(current_user["type"])
#     all_products = await admin_get_products(owner_id, skip=0)
#     return all_products

# @app.get("allUsers") #it will list the all users
# @app.get("users/products/{id}") #this will show all users producst  store
# @app.get("AllProducts") #this will show all products store so far in the @app.get("/AllProducts/", response_model= list[ProductResponse])

# async def lavdalasoon():
#     pass
