import os

from dotenv import load_dotenv

from pymongo import MongoClient

from pymongo.errors import (
    PyMongoError,
    ServerSelectionTimeoutError
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

MONGO_URI = os.getenv(
    "MONGO_URI"
)

DATABASE_NAME = os.getenv(
    "MONGO_DATABASE",
    "handwritten_ocr"
)

COLLECTION_NAME = os.getenv(
    "MONGO_COLLECTION",
    "ocr_records"
)


# ============================================================
# VALIDATE MONGO URI
# ============================================================

if not MONGO_URI:

    raise RuntimeError(
        "MONGO_URI is not configured "
        "in the .env file."
    )


# ============================================================
# MONGODB CLIENT
# ============================================================

client = MongoClient(
    MONGO_URI,

    serverSelectionTimeoutMS=5000
)


# ============================================================
# DATABASE
# ============================================================

db = client[
    DATABASE_NAME
]


# ============================================================
# OCR COLLECTION
# ============================================================

ocr_collection = db[
    COLLECTION_NAME
]


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database() -> bool:

    try:

        client.admin.command(
            "ping"
        )

        return True


    except (
        ServerSelectionTimeoutError,
        PyMongoError
    ) as error:

        print(
            "MongoDB connection error:",
            error
        )

        return False