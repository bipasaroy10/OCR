import os
import sys
import time
import json
import mimetypes

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "images"
)

RESULT_DIR = os.path.join(
    BASE_DIR,
    "results",
    "gemini"
)

METADATA_FILE = os.path.join(
    RESULT_DIR,
    "metadata.json"
)


# ============================================================
# GEMINI ENVIRONMENT
# ============================================================

# Your Gemini project is:
#
# gemini-service/
# └── backend/
#     └── .env
#
# So we load that .env file here.

GEMINI_ENV_FILE = os.path.join(
    BASE_DIR,
    "..",
    "gemini-service",
    "backend",
    ".env"
)

load_dotenv(GEMINI_ENV_FILE)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found.\n"
        f"Expected .env at:\n{GEMINI_ENV_FILE}"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# OCR PROMPT
# ============================================================

OCR_PROMPT = """
You are an OCR system specialized in handwritten documents.

Read the handwritten text in the provided image.

Instructions:

1. Extract ONLY the text that is actually visible.
2. Preserve the original wording as accurately as possible.
3. Preserve paragraphs and line breaks where possible.
4. Preserve numbers, dates, symbols, and punctuation.
5. Do not summarize the content.
6. Do not explain the image.
7. Do not add information that is not present.
8. Do not correct grammar or spelling.
9. If handwriting is unclear, make the best possible interpretation.
10. Return ONLY the extracted text.

Do not add markdown.
Do not add explanations.
Do not add comments.
"""


# ============================================================
# SUPPORTED IMAGE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp"
}


# ============================================================
# CREATE RESULT DIRECTORY
# ============================================================

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

def process_image(
    image_path: str
):

    filename = os.path.basename(
        image_path
    )

    image_id = os.path.splitext(
        filename
    )[0]

    extension = os.path.splitext(
        filename
    )[1].lower()

    mime_type = SUPPORTED_EXTENSIONS.get(
        extension
    )

    if not mime_type:
        print(
            f"Skipping unsupported file: {filename}"
        )

        return None

    print(
        f"\nProcessing: {filename}"
    )

    try:

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        with open(
            image_path,
            "rb"
        ) as image_file:

            image_bytes = image_file.read()


        # ----------------------------------------------------
        # Start timer
        # ----------------------------------------------------

        start_time = time.perf_counter()


        # ----------------------------------------------------
        # Send image to Gemini
        # ----------------------------------------------------

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                ),

                OCR_PROMPT
            ]
        )


        # ----------------------------------------------------
        # End timer
        # ----------------------------------------------------

        end_time = time.perf_counter()

        processing_time = (
            end_time - start_time
        )


        # ----------------------------------------------------
        # Get response
        # ----------------------------------------------------

        extracted_text = (
            response.text or ""
        ).strip()


        if not extracted_text:

            print(
                f"WARNING: Gemini returned empty text "
                f"for {filename}"
            )

            extracted_text = ""


        # ----------------------------------------------------
        # Save text result
        # ----------------------------------------------------

        output_file = os.path.join(
            RESULT_DIR,
            f"{image_id}.txt"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                extracted_text
            )


        # ----------------------------------------------------
        # Create metadata
        # ----------------------------------------------------

        result = {

            "image_id": image_id,

            "filename": filename,

            "model": MODEL_NAME,

            "processing_time_seconds":
                round(
                    processing_time,
                    4
                ),

            "text_length":
                len(extracted_text),

            "success": True

        }


        print(
            f"Completed: {filename}"
        )

        print(
            f"Time: {processing_time:.2f} seconds"
        )

        print(
            f"Output: {output_file}"
        )


        return result


    except Exception as error:

        print(
            f"ERROR processing {filename}:"
        )

        print(
            str(error)
        )


        return {

            "image_id": image_id,

            "filename": filename,

            "model": MODEL_NAME,

            "processing_time_seconds": None,

            "text_length": 0,

            "success": False,

            "error": str(error)

        }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=========================================="
    )

    print(
        "       GEMINI OCR BENCHMARK"
    )

    print(
        "=========================================="
    )

    print(
        f"Model: {MODEL_NAME}"
    )

    print(
        f"Image directory: {IMAGE_DIR}"
    )

    print(
        f"Result directory: {RESULT_DIR}"
    )


    # --------------------------------------------------------
    # Check image directory
    # --------------------------------------------------------

    if not os.path.exists(
        IMAGE_DIR
    ):

        print(
            "\nERROR: Dataset image directory "
            "does not exist."
        )

        print(
            IMAGE_DIR
        )

        sys.exit(1)


    # --------------------------------------------------------
    # Find images
    # --------------------------------------------------------

    image_files = []

    for filename in os.listdir(
        IMAGE_DIR
    ):

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension in SUPPORTED_EXTENSIONS:

            image_files.append(
                filename
            )


    image_files.sort()


    if not image_files:

        print(
            "\nNo supported images found."
        )

        print(
            "Put JPG, PNG or WEBP images inside:"
        )

        print(
            IMAGE_DIR
        )

        sys.exit(1)


    print(
        f"\nFound {len(image_files)} images."
    )


    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    all_results = []


    for index, filename in enumerate(
        image_files,
        start=1
    ):

        print(
            f"\n[{index}/{len(image_files)}]"
        )

        image_path = os.path.join(
            IMAGE_DIR,
            filename
        )

        result = process_image(
            image_path
        )

        if result:

            all_results.append(
                result
            )


    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_results,
            file,
            indent=4,
            ensure_ascii=False
        )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    successful = sum(
        1
        for result in all_results
        if result["success"]
    )

    failed = len(all_results) - successful


    print(
        "\n=========================================="
    )

    print(
        "             BENCHMARK COMPLETE"
    )

    print(
        "=========================================="
    )

    print(
        f"Total images : {len(all_results)}"
    )

    print(
        f"Successful   : {successful}"
    )

    print(
        f"Failed       : {failed}"
    )

    print(
        f"\nResults saved in:"
    )

    print(
        RESULT_DIR
    )

    print(
        f"\nMetadata saved in:"
    )

    print(
        METADATA_FILE
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()