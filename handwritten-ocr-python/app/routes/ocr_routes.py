import os
import shutil
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException
)

from services.ocr_processor import process_file

from services.ocr_repository import (
    get_all_ocr_records,
    get_ocr_by_id
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"]
)


# ============================================================
# PROJECT DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".pdf"
}


# ============================================================
# POST OCR
# ============================================================

@router.post("")
async def upload_and_ocr(
    file: UploadFile = File(...)
):

    file_path = None

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed: JPG, JPEG, PNG, "
                "WEBP, BMP, PDF."
            )
        )


    # --------------------------------------------------------
    # Generate temporary filename
    # --------------------------------------------------------

    unique_name = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )


    file_path = (
        UPLOAD_DIR /
        unique_name
    )


    try:

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        print(
            f"\nProcessing file: "
            f"{file.filename}"
        )

        print(
            f"Temporary file: "
            f"{file_path}"
        )


        # ----------------------------------------------------
        # OCR PROCESSING
        # ----------------------------------------------------

        record = process_file(
            file_path=str(file_path),
            original_name=file.filename,
            mime_type=file.content_type
        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,

            "message": (
                "OCR completed successfully."
            ),

            "data": record
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "OCR ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        # ----------------------------------------------------
        # Close uploaded file
        # ----------------------------------------------------

        try:

            await file.close()

        except Exception as error:

            print(
                "FILE CLOSE ERROR:",
                repr(error)
            )


        # ----------------------------------------------------
        # Delete temporary uploaded file
        # ----------------------------------------------------

        if (
            file_path is not None
            and file_path.exists()
        ):

            try:

                file_path.unlink()

                print(
                    f"Temporary file deleted: "
                    f"{file_path}"
                )

            except Exception as error:

                print(
                    "UPLOAD CLEANUP ERROR:",
                    repr(error)
                )


# ============================================================
# GET OCR HISTORY
# ============================================================

@router.get("/history")
def ocr_history():

    try:

        records = get_all_ocr_records()


        return {
            "success": True,

            "count": len(records),

            "data": records
        }


    except Exception as error:

        print(
            "HISTORY ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# GET ONE OCR RESULT
# ============================================================

@router.get("/{record_id}")
def get_single_ocr(
    record_id: str
):

    try:

        record = get_ocr_by_id(
            record_id
        )


        if not record:

            raise HTTPException(
                status_code=404,
                detail="OCR record not found."
            )


        return {
            "success": True,

            "data": record
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "GET OCR ERROR:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )