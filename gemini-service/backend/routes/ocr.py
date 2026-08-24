from fastapi import APIRouter, UploadFile, File, HTTPException

from services.gemini_ocr import extract_handwritten_text


router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"]
)


@router.post("/handwritten")
async def handwritten_ocr(
    file: UploadFile = File(...)
):
    try:

        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG and WEBP images are supported"
            )

        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        extracted_text = extract_handwritten_text(
            image_bytes=image_bytes,
            mime_type=file.content_type
        )

        return {
            "success": True,
            "filename": file.filename,
            "text": extracted_text
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "HANDWRITTEN OCR ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract handwritten text: {str(e)}"
        )