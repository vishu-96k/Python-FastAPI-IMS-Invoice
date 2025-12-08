# In short:
# This file is your authentication guard.
# It checks the JWT coming from the client, verifies it, finds the user in the database, and returns the safe user object to protected routes.
#The function verifies the JWT using jwt.decode() to make sure the token is real, valid, and not expired. After that, it fetches the user from the database and returns the user’s safe data (without password) to the protected route.

from fastapi.security import HTTPBearer # security = HTTPBearer()

from fastapi import Depends, HTTPException, status # Import FastAPI dependencies and exceptions

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # HTTPBearer is a security class to extract token from Authorization header  # HTTPAuthorizationCredentials stores the token string

from .jwt_handler import JWT_SECRET, JWT_ALGORITHM  # Import JWT settings

from ..database import users_collection # Import MongoDB users collection

from bson.objectid import ObjectId # Convert string id to ObjectId for MongoDB queries

import jwt # PyJWT library for decoding JWT tokens, and verifying it

security = HTTPBearer(auto_error=False)  # Create a reusable security object for extracting the token, if no token exsists then aslo it will work

# -------------------------------
# Function to get current user
# -------------------------------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):   # `credentials` = the token extracted from Authorization header by HTTPBearer # Depends() is a FastAPI feature that injects dependencies into your function automatically. and security is the class or function that you r depending on
    print("\n===== AUTH DEBUG START =====")

    if credentials is None:  #check if the authorization header is none
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = credentials.credentials  # Extract the actual JWT string (the part after "Bearer") from the client request Auth HEADER
    print("🔹 Received Token:", token)

           
    try:   #verification of the token, with the server token and the client token happens here, using the built in fuinction library
        decoded = jwt.decode(            # Decode the JWT to read payload and verify signature
            token,                       # The JWT string sent by client
            JWT_SECRET,                  # Secret key used to verify the signature
            algorithms=[JWT_ALGORITHM]   # Algorithm used to sign and validate JWT (e.g., HS256) 
            #  jwt.decode() performs these checks:
            # FastAPI/PyJWT takes the token you sent and:
            # Extracts header + payload
            # Recomputes the signature using your JWT_SECRET
            # Compares it with the signature inside the token           
        )
        print("🔹 Decoded JWT:", decoded) #decode will have the deacoded secrate key
     

        user_id = decoded.get("sub")    # Extract user_id (stored in the "sub" claim)
        print("🔹 Extracted user_id:", user_id)

    except Exception as e:  # If decoding fails (expired, invalid signature, fake token)
        print("❌ JWT decode error:", e)
        print("===== AUTH DEBUG END =====")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fetch user from DB
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)}) # Fetch user from MongoDB using user_id # Convert user_id string → ObjectId

        print("🔹 User from DB:", user)
    except Exception as e:
        print("❌ DB lookup failed:", e)
        print("===== AUTH DEBUG END =====")
        raise HTTPException(status_code=401, detail="User lookup failed")

    if not user:    # If no such user exists in DB
        print("❌ User not found in DB")  
        print("===== AUTH DEBUG END =====")
        raise HTTPException(status_code=401, detail="User not found")

    # Cleanup & return
    user["_id"] = str(user["_id"])
    user.pop("password", None)

    print("✅ Final sanitized user:", user)
    print("===== AUTH DEBUG END =====\n")

    return user


async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This function allows optional authentication:
    # - If token exists and is valid → return user
    # - If no token or invalid token → return None

    if credentials:
        token = credentials.credentials  # Extract token
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])    # Decode token
            user_id = decoded.get("sub")  # Extract user_id frommthe token
            from ..database import users_collection    # Fetch user from DB
            from bson.objectid import ObjectId
            user = await users_collection.find_one({"_id": ObjectId(user_id)})   # Finds the user id in the database, which is been extracted from token
            if user:
                user["_id"] = str(user["_id"])
                user.pop("password", None)
                return user
        except:
            pass
    return None 
"""
Valid token & existing user: returns the user object from the database (without password).
No token or invalid token: returns None.    
"""
"""
----------------EXTRATING JWT TOKEN FROM ROUTES------------------------
get_current_user() → Token required, verify token, fetch user, return user.
get_optional_user() → Token optional, return user if token valid, otherwise None.

✅ What this file/function does (short version)
Extracts JWT token from the request header.
Verifies and decodes the token using the secret & algorithm.
Fetches the corresponding user from the MongoDB database.
Removes sensitive fields (like password).
Returns current user data to use in routes.

✅ Why we need this file/function
Provides a FastAPI dependency for protected routes.
Ensures only authenticated users can access certain APIs.
Centralizes token verification logic — no need to repeat in every route.
Automatically prevents unauthorized access (401 errors).

"""
"""
✅What get_current_user() : 
Extracts the JWT token from the Authorization: Bearer <token> header.
Decodes the token using the secret + algorithm.
Reads the user_id (sub) inside the token.
Looks up the user in MongoDB using that user_id.
Removes the password from the user data.
Returns the authenticated user to the route.
If anything goes wrong (invalid token, expired token, user not found), it throws 401 Unauthorized.
This function is used in protected routes like: 
    @router.get("/profile") 
    async def get_profile(current_user = Depends(get_current_user)):
    return current_user
    
#✅ What Depends(security) actually does internally?
#     Call → /profile
# |
# |--- Run security() first
# |      |
# |      Extract token
# |      Validate header
# |      If missing → return 403/401
# |
# |--- Then run get_profile()
#        |
#        Pass token to parameter "user"    

✅What get_optional_user()
It works the same way as get_current_user(), but token is optional.
If token is valid → returns user
If token is missing or invalid → returns None (no error)
"""


