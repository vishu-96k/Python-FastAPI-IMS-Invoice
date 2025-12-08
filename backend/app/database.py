# database.py
# Connects to MongoDB Atlas using async Motor which is a driver for mongo db.
#This is the recommended Motor setup used in real production FastAPI apps.


from motor.motor_asyncio import AsyncIOMotorClient   # Import async MongoDB client (Motor driver)
from decouple import config                           # Import config to read values from .env file, helps to take data from the .env file

MONGO_URL = config("MONGO_URL")                       # Read MongoDB connection URL from .env
DB_NAME = config("DB_NAME")                           # Read database name from .env

client = AsyncIOMotorClient(MONGO_URL)                 #AsyncIOMotorClient is a class which creates conn to mongodb cluster and when uh make "clinet" object it creats mongodb connection, Clent is noth but uh can say mongo db Cluster Object

db = client[DB_NAME]                                  # Select the database we want to use

users_collection = db.get_collection("users")         # Get reference to 'users' collection
products_collection = db.get_collection("products")   # Get reference to 'products' collection
invoices_collection = db.get_collection("invoices")   # Get reference to 'invoices' collection

# -----------------------------------------------
# ✅ What happens here (in simple points)

# 1️⃣ AsyncIOMotorClient(MONGO_URL)
# Uses the MongoDB driver (Motor) to connect to your MongoDB server.
# MONGO_URL contains your connection string like: mongodb+srv://username:password@cluster.mongodb.net
# This line does NOT create a database, it only connects to your MongoDB cluster.
# It creates a client object (like a doorway to the database server).
# All future database operations use this client.

# 2️⃣ client[DB_NAME]
# Selects the database name you want to use.
# If the database does NOT exist, MongoDB automatically creates it when you insert the first document.
# This line returns a database object, not data.
# This object is used to get collections and run CRUD queries.


# 1️⃣ client = MongoDB Client Object (basically cluster object)
# Represents the connection to the MongoDB server.
# Example: connecting to your MongoDB Atlas cluster.
# Think of it like: the main door to the building.

# 2️⃣ db = Database Object (basically database object)
# db = client[DB_NAME]
# This gives you a reference to ONE database inside the server.
# Think of it like: a room inside the building.

# 3️⃣ collection = Collection Object (basically collectios object using which uh will fire the queries)
# Example: users_collection = db.get_collection("users")
# This refers to a table-like folder that stores documents.
# Think of it like: a file drawer inside the room.


# ✅ What is AsyncIOMotorClient? : AsyncIOMotorClient = Driver class that connects Python → MongoDB
# 👉 It is a class provided by Motor (MongoDB async driver).
# 👉 This class creates a connection to MongoDB.


# ⭐ How MongoDB Connection Works (easy explanation)
# You give the URL (MONGO_URL) → tells where your MongoDB is hosted.
# Client connects to MongoDB cluster using that URL.
# Database is selected using client[DB_NAME].
# From that database, you select collections like:
# db.get_collection("users")
# db.get_collection("products")
# This is how your FastAPI app talks to MongoDB.

# 💡 Super Simple Analogy
# AsyncIOMotorClient = you are entering the MongoDB building.
# client[DB_NAME] = you walk into a specific room (database).
# db.get_collection("users") = you open a specific drawer (collection).