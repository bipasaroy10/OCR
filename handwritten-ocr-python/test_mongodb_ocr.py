from database import check_database

from services.ocr_repository import (
    create_ocr_record
)


print("=" * 60)
print("OCR → MONGODB TEST")
print("=" * 60)


# ------------------------------------------------------------
# Check MongoDB
# ------------------------------------------------------------

if not check_database():

    raise RuntimeError(
        "MongoDB connection failed."
    )


# ------------------------------------------------------------
# Example OCR text
# ------------------------------------------------------------

ocr_text = """
This is a handwritten OCR test.

Unlimited-OCR successfully recognized
this text from the document.
"""


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

record = create_ocr_record(

    original_name=
        "handwritten-note.jpeg",

    file_size=
        52393,

    mime_type=
        "image/jpeg",

    ocr_text=
        ocr_text,

    page_count=
        1
)


print("\nOCR record saved successfully.")

print("\nMongoDB ID:")

print(
    record["_id"]
)


print("\nOCR Text:")

print(
    record["ocrText"]
)


print("\nCreated At:")

print(
    record["createdAt"]
)


print("\n" + "=" * 60)