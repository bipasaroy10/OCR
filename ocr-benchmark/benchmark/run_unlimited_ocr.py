import os
import sys
import time
import json

import requests


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
    "unlimited_ocr"
)

METADATA_FILE = os.path.join(
    RESULT_DIR,
    "metadata.json"
)


# ============================================================
# BAIDU OCR SERVER
# ============================================================

OCR_URL = "http://localhost:5000/api/ocr"


# ============================================================
# CREATE RESULT DIRECTORY
# ============================================================

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


# ============================================================
# SUPPORTED IMAGE EXTENSIONS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}


# ============================================================
# EXTRACT OCR TEXT
# ============================================================

def extract_text_from_response(response):

    try:

        data = response.json()

    except ValueError:

        return response.text.strip()


    if isinstance(data, str):

        return data.strip()


    if isinstance(data, dict):

        possible_keys = [
            "text",
            "result",
            "output",
            "ocr_text",
            "extracted_text"
        ]

        # ----------------------------------------------------
        # Check top-level response
        # ----------------------------------------------------

        for key in possible_keys:

            value = data.get(key)

            if isinstance(value, str):

                return value.strip()


        # ----------------------------------------------------
        # Check nested data
        # ----------------------------------------------------

        nested_data = data.get("data")

        if isinstance(
            nested_data,
            dict
        ):

            for key in possible_keys:

                value = nested_data.get(key)

                if isinstance(value, str):

                    return value.strip()


        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        return json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )


    return str(data)


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

def process_image(image_path):

    filename = os.path.basename(
        image_path
    )

    image_id = os.path.splitext(
        filename
    )[0]

    print(
        f"\nProcessing: {filename}"
    )


    try:

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        with open(
            image_path,
            "rb"
        ) as image_file:

            # IMPORTANT:
            #
            # Your FastAPI endpoint expects:
            #
            # file: UploadFile = File(...)
            #
            # Therefore the multipart field MUST be:
            #
            # "file"
            #

            files = {
                "file": (
                    filename,
                    image_file,
                    "application/octet-stream"
                )
            }


            # ------------------------------------------------
            # Start timer
            # ------------------------------------------------

            start_time = time.perf_counter()


            # ------------------------------------------------
            # Send request
            # ------------------------------------------------

            response = requests.post(
                OCR_URL,
                files=files,
                timeout=300
            )


            # ------------------------------------------------
            # End timer
            # ------------------------------------------------

            end_time = time.perf_counter()

            processing_time = (
                end_time - start_time
            )


        # ====================================================
        # HANDLE HTTP ERRORS
        # ====================================================

        if response.status_code != 200:

            print(
                f"HTTP {response.status_code}"
            )

            print(
                "Server response:"
            )

            print(
                response.text
            )

            return {
                "image_id": image_id,
                "filename": filename,
                "model": "baidu/Unlimited-OCR",
                "processing_time_seconds": round(
                    processing_time,
                    4
                ),
                "text_length": 0,
                "success": False,
                "error": (
                    f"HTTP {response.status_code}: "
                    f"{response.text}"
                )
            }


        # ====================================================
        # EXTRACT OCR TEXT
        # ====================================================

        extracted_text = (
            extract_text_from_response(
                response
            )
        )


        # ====================================================
        # SAVE OCR RESULT
        # ====================================================

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


        # ====================================================
        # RESULT METADATA
        # ====================================================

        result = {

            "image_id": image_id,

            "filename": filename,

            "model": "baidu/Unlimited-OCR",

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
            f"Time: "
            f"{processing_time:.2f} seconds"
        )

        print(
            f"Output: "
            f"{output_file}"
        )


        return result


    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except requests.exceptions.ConnectionError:

        print(
            "\nERROR: Cannot connect to "
            "Baidu OCR server."
        )

        print(
            f"Expected endpoint:"
        )

        print(
            OCR_URL
        )

        print(
            "Make sure handwritten-ocr-python "
            "is running on port 5000."
        )


        return {

            "image_id": image_id,

            "filename": filename,

            "model": "baidu/Unlimited-OCR",

            "processing_time_seconds": None,

            "text_length": 0,

            "success": False,

            "error":
                "Baidu OCR server unavailable"

        }


    # ========================================================
    # TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout:

        print(
            f"ERROR: OCR timeout for "
            f"{filename}"
        )


        return {

            "image_id": image_id,

            "filename": filename,

            "model": "baidu/Unlimited-OCR",

            "processing_time_seconds": None,

            "text_length": 0,

            "success": False,

            "error":
                "OCR request timed out"

        }


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as error:

        print(
            f"ERROR processing "
            f"{filename}:"
        )

        print(
            repr(error)
        )


        return {

            "image_id": image_id,

            "filename": filename,

            "model": "baidu/Unlimited-OCR",

            "processing_time_seconds": None,

            "text_length": 0,

            "success": False,

            "error":
                str(error)

        }


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "       UNLIMITED-OCR BENCHMARK"
    )

    print(
        "=" * 60
    )

    print(
        "Model: baidu/Unlimited-OCR"
    )

    print(
        f"Server: {OCR_URL}"
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

        sys.exit(1)


    print(
        f"\nFound "
        f"{len(image_files)} images."
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
            f"\n[{index}/"
            f"{len(image_files)}]"
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

    failed = (
        len(all_results)
        - successful
    )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "          BENCHMARK COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"Total images : "
        f"{len(all_results)}"
    )

    print(
        f"Successful   : "
        f"{successful}"
    )

    print(
        f"Failed       : "
        f"{failed}"
    )

    print(
        "\nResults saved in:"
    )

    print(
        RESULT_DIR
    )

    print(
        "\nMetadata saved in:"
    )

    print(
        METADATA_FILE
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()