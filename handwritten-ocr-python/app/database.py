import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "handwritten_ocr"
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "ocr_results"
)

client = MongoClient(MONGODB_URI)

db = client[DATABASE_NAME]

ocr_collection = db[COLLECTION_NAME]


def check_database():

    try:
        client.admin.command("ping")
        print("MongoDB connected successfully")
        return True

    except Exception as e:

        print("MongoDB connection failed:", e)
        return False