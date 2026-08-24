from datetime import datetime, timezone

from bson import ObjectId

from database import ocr_collection


# ============================================================
# CREATE OCR RECORD
# ============================================================

def create_ocr_record(
    original_name: str,
    file_size: int,
    mime_type: str | None,
    ocr_text: str,
    page_count: int,
    model_name: str = "baidu/Unlimited-OCR"
):
    """
    Store an OCR result in MongoDB.
    """

    document = {
        "originalName": original_name,
        "fileSize": file_size,
        "mimeType": mime_type,
        "ocrText": ocr_text,
        "pageCount": page_count,
        "model": model_name,
        "createdAt": datetime.now(timezone.utc)
    }


    result = ocr_collection.insert_one(
        document
    )


    document["_id"] = str(
        result.inserted_id
    )


    return document


# ============================================================
# GET ALL OCR RECORDS
# ============================================================

def get_all_ocr_records():
    """
    Return all OCR records, newest first.
    """

    records = (
        ocr_collection
        .find({})
        .sort(
            "createdAt",
            -1
        )
    )


    result = []


    for record in records:

        record["_id"] = str(
            record["_id"]
        )


        result.append(
            record
        )


    return result


# ============================================================
# GET ONE OCR RECORD
# ============================================================

def get_ocr_by_id(
    record_id: str
):
    """
    Return one OCR record by MongoDB ObjectId.
    """

    # --------------------------------------------------------
    # Validate ObjectId
    # --------------------------------------------------------

    if not ObjectId.is_valid(
        record_id
    ):

        return None


    object_id = ObjectId(
        record_id
    )


    # --------------------------------------------------------
    # Find record
    # --------------------------------------------------------

    record = (
        ocr_collection
        .find_one(
            {
                "_id": object_id
            }
        )
    )


    # --------------------------------------------------------
    # Convert ObjectId to string
    # --------------------------------------------------------

    if record:

        record["_id"] = str(
            record["_id"]
        )


    return record