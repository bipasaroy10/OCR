import os

from services.ocr_service import OCRService

from services.ocr_repository import (
    create_ocr_record
)


# ============================================================
# OCR SERVICE INSTANCE
# ============================================================

ocr_service = OCRService()


# ============================================================
# PROCESS FILE
# ============================================================

def process_file(
    file_path: str,
    original_name: str,
    mime_type: str | None
):
    """
    Process an uploaded image/PDF using Unlimited-OCR
    and save the extracted text to MongoDB.
    """

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )


    # --------------------------------------------------------
    # Get file size
    # --------------------------------------------------------

    file_size = os.path.getsize(
        file_path
    )


    # --------------------------------------------------------
    # Run OCR
    # --------------------------------------------------------

    result = ocr_service.extract_text(
        file_path
    )


    if not isinstance(result, dict):

        raise RuntimeError(
            "OCR service returned an invalid result."
        )


    # --------------------------------------------------------
    # Extract OCR information
    # --------------------------------------------------------

    ocr_text = result.get(
        "text",
        ""
    )


    page_count = result.get(
        "page_count",
        1
    )


    # --------------------------------------------------------
    # Validate OCR result
    # --------------------------------------------------------

    if not ocr_text:

        print(
            "WARNING: OCR returned empty text."
        )


    # --------------------------------------------------------
    # Save result to MongoDB
    # --------------------------------------------------------

    record = create_ocr_record(

        original_name=original_name,

        file_size=file_size,

        mime_type=mime_type,

        ocr_text=ocr_text,

        page_count=page_count
    )


    # --------------------------------------------------------
    # Return database record
    # --------------------------------------------------------

    return record