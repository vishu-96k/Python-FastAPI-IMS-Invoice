#this file incldues the logic, matlb the PRODUCTS_ROUTES, will call these functins to do CURD operations on producs, and these fucntions will take the data from the RPODUCT_API_ROUTES, Create the producst, store them in the database, and return a responce to the API

from bson import ObjectId
from app.database import products_collection, users_collection
from datetime import datetime
from fastapi import HTTPException

#PRODUCT IS VALUD OR NOT CHECKING
def validate_object_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    return ObjectId(id)

# CREATE PRODUCT
async def create_product(owner_id: str, product_data: dict):
    product_data["owner_id"] = ObjectId(owner_id)
    product_data["created_at"] = datetime.utcnow()
    res = await products_collection.insert_one(product_data)
    prod = await products_collection.find_one({"_id": res.inserted_id})
    prod["_id"] = str(prod["_id"]) #converting the product id into string
    prod["owner_id"] = str(prod["owner_id"]) #converting the product owner id into string
    return prod


# GETTING ALL PRODUCT
async def get_products(owner_id: str, skip: int = 0):
    cursor = products_collection.find(
        {"owner_id": ObjectId(owner_id)}
    ).skip(skip)

    products = []
    async for product in cursor:
        product["_id"] = str(product["_id"])
        product["owner_id"] = str(product["owner_id"])
        products.append(product)

    return products

#GETTING A SINGLE PRODUCT
async def get_product(owner_id: str, product_id: str):
    product_obj_id = validate_object_id(product_id)

    product = await products_collection.find_one({"_id": product_obj_id})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check ownership
    if product["owner_id"] != ObjectId(owner_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this product")

    product["_id"] = str(product["_id"])
    product["owner_id"] = str(product["owner_id"])

    return product

# UPDATE PRODUCT (PARTIAL)
async def update_product(owner_id: str, product_id: str, updates: dict):
    product_obj_id = validate_object_id(product_id)

    # Only fields provided in updates are changed
    updates = {k: v for k, v in updates.items() if v is not None}

    # Check product exists
    product = await products_collection.find_one({"_id": product_obj_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Owner check
    if product["owner_id"] != ObjectId(owner_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    await products_collection.update_one(
        {"_id": product_obj_id},
        {"$set": updates}
    )

    # Fetch updated product
    updated_product = await products_collection.find_one({"_id": product_obj_id})

    updated_product["_id"] = str(updated_product["_id"])
    updated_product["owner_id"] = str(updated_product["owner_id"])

    return updated_product


# DELETE PRODUCT
async def delete_product(owner_id: str, product_id: str):
    product_obj_id = validate_object_id(product_id)

    product = await products_collection.find_one({"_id": product_obj_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Owner check
    if product["owner_id"] != ObjectId(owner_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    await products_collection.delete_one({"_id": product_obj_id})

    #returing the deleted product info
    product["_id"] = str(product["_id"])
    product["owner_id"] = str(product["owner_id"])
    return product   # You can also return a message if you want





































#------------ADMIN ROUTES-----------OPERATAIOSN ------------
#GETTING ALL PRODUCTS
# async def admin_get_products(owner_id: str, skip: int = 0):

#     #Checking of user as admin or not
#     user = await users_collection.find_one({"_id":owner_id})
#     TYPE = "admin"
#     if user["type"]!=TYPE:
#         raise HTTPException(status_code=403, detail="Not authorized to delete this product")

#     #query databse for detching all the products itesm    
#     # cursor = products_collection.find(
#     #     {"owner_id": ObjectId(owner_id)}
#     # ).skip(skip)
#     Iteams = await products_collection.find().skip(skip).to_list()

#     products = []
#     async for product in Iteams:
#         product["_id"] = str(product["_id"])
#         product["owner_id"] = str(product["owner_id"])
#         product["name"] = str(product["name"])
#         products.append(product)

#     return products