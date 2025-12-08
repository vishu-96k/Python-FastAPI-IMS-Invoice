# hashing.py → hash/verify password
# ✅ 1. hashing.py (Password Hashing With Bcrypt)
#inshot : this functions hass the password to store it in the database, becoz plain password is not safe, and also when the user enters the passwords, the for de-hasing the password and verifuying it also we use this functions

# Import CryptContext from passlib
# Passlib is a library used for hashing and verifying passwords safely.
from passlib.context import CryptContext

# Create a CryptContext object
# - schemes=["bcrypt"] → we are using bcrypt hashing algorithm
# - deprecated="auto" → old hashing methods will automatically be updated
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Function 1: Hash the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Function 2: Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


"""
This file functionality :
    1)Add haskey in the password
    2)verify the user inputed passwird with the database passeword of that user

Use this to hash and verify user passwords before storing them in MongoDB.

CryptContext : this library Creates a password hashing engine
CryptContext helps manage password hashing algorithms like bcrypt.
"""
"""
1️⃣ hash_password(password: str) → str
What it does: Converts a plain-text password into a secure hashed string using bcrypt.
Why: Storing plain passwords in the database is dangerous. If the DB is leaked, users’ passwords are exposed.
Usage: Call this before saving a user’s password to the databas

2️⃣ verify_password(plain_password, hashed_password) → bool
What it does: Checks if a plain-text password matches the hashed password stored in the DB.
Why: Allows authentication without ever storing or comparing plain passwords.
Usage: Call this when a user logs in to verify their password.
"""