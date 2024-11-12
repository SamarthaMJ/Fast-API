from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

# Load environment variables from .env file if needed
load_dotenv()

# MongoDB URI from environment variable or fallback to localhost
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Attempt to connect to MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Force a request to the server to verify connection
    client.server_info()
    print("Successfully connected to MongoDB!")
    
    # List databases as a simple test
    databases = client.list_database_names()
    print("Databases:", databases)

except ServerSelectionTimeoutError as e:
    print("Could not connect to MongoDB:", e)
