
# 1. user_model.py (MongoDB Document Structure)
# This ( MODLES ) file is ONLY for reference + consistency. We dont have any dependency with this model files
# MongoDB does NOT enforce schema, but you maintain structure here basially like a tble struture as uh have in SQL (SQL follows schema).
# this file is NOT used by FastAPI or the database.
# It is only a reference file made by you to understand the MongoDB structure.


# MongoDB is schema-less → it does NOT use models like SQL.
# So you created this file only to document your expected structure.

# app/models/user_model.py

from datetime import datetime
from bson import ObjectId

# Helper class to convert MongoDB ObjectId → string
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate    # This tells Pydantic to use validate() to check the value
    
    @classmethod
    def validate(cls, v):
        return str(v)         # Converts ObjectId to string so JSON can return it cleanly
        

# MongoDB Document Model (for reference)
UserDocument = {
    "_id": "ObjectId",        # Unique ID that MongoDB creates
    "name": "string",         # User's full name
    "email": "string",        # User's email address
    "password": "hashed string",  # Saved password (hashed)
    "created_at": "datetime"  # When the user was created
}


# ------------------------------------
# ⭐ Simple Explanation of user_model.py
# This file does NOT enforce any schema in MongoDB.
# MongoDB does not require a model → it is schema-less.
# You created this file only as a documentation reference.
# The class PyObjectId is a utility to convert MongoDB ObjectId to string.
# UserDocument is a fake schema to show how the document will look.
