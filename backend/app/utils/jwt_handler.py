# In short:
# This file generates the “key” (JWT token) every user needs to access protected API endpoints safely.
# In short: It creates a secure, time-limited token for a user, which proves their identity when accessing APIs.

from datetime import datetime, timedelta     # Used to set issued time (iat) and expiry time (exp)
from decouple import config                  # Used to read values from .env file
import jwt                                   # PyJWT library used to create/encode JWT tokens


# Load secret key from .env (used to sign the JWT)
JWT_SECRET = config("JWT_SECRET")

# Algorithm used to sign and verify the token (HS256 = secure and common)
JWT_ALGORITHM = "HS256"

# Token expiry time in minutes (here: 60 minutes / 1 hour)
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Function to create JWT access token
def create_access_token(user_id: str):

    # 1. Calculate expiry time for the token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)   # datetime.utcnow() → current time in UTC     # timedelta(...) → add 60 minutes to current time
    
    # 2. Create the JWT payload (data to stored inside the token)
    payload = {
        "sub": user_id,            # "sub" = subject = usually the user ID
        "exp": expire,             # Token expiry time (JWT will auto-expire)
        "iat": datetime.utcnow()   # "iat" = issued-at time (when token was created)
    }

   
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)  # 3. Encode the payload using SECRET + ALGORITHM     # Returns a signed JWT token (string)

"""
--------------------------------- JWT EXPLANTION ----------------------------
✅ create_access_token function:
What it does: Generates a JWT token for a user to access protected API routes.

Why we use it:
    To authenticate users without storing session info on the server.
    Ensures secure, tamper-proof communication between client and server.
    Encodes user ID and token expiry inside the token.

function Returns value: A JWT token string, e.g.:
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....
    This token can be sent by the client to access protected routes

✅ What this file does
Creates JWT access tokens for users after they log in.
Each token contains:
sub → user ID
exp → expiry time
iat → issued-at time
Signs the token using JWT_SECRET + HS256 so it cannot be tampered.
Returns a string token to the frontend.

✅ Why we need this file
To authenticate users without storing sessions on the server.
Ensures secure API access: only users with valid tokens can access protected routes.
Automatically handles token expiry, improving security.
"""
