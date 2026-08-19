import os
import re
import uuid
import shutil
import tempfile

import torch
import fitz  # PyMuPDF

from flask import Flask, request, jsonify
from flask_cors import CORS

from transformers import AutoModel, AutoTokenizer


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "baidu/Unlimited-OCR"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "api_uploads"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "api_outputs"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Flask
# ============================================================

app = Flask(__name__)

CORS(app)

# Maximum upload size: 50 MB
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


# ============================================================
# Load Unlimited-OCR
# ============================================================

print("=" * 60)
print("Loading Unlimited-OCR")
print("=" * 60)

print("PyTorch:", torch.__version__)

print(
    "CUDA available:",
    torch.cuda.is_available()
)

if not torch.cuda.is_available():

    raise RuntimeError(
        "CUDA is not available. "
        "Unlimited-OCR requires a CUDA-capable NVIDIA GPU."
    )


GPU_NAME = torch.cuda.get_device_name(0)

GPU_MEMORY = (
    torch.cuda.get_device_properties(0).total_memory
    / 1024**3
)

print("GPU:", GPU_NAME)

print(
    f"VRAM: {GPU_MEMORY:.2f} GB"
)


# ============================================================
# Tokenizer
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("Tokenizer loaded.")


# ============================================================
# Model
# ============================================================

print("\nLoading model...")

model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch.bfloat16
)

model = model.eval().cuda()

print("Unlimited-OCR loaded successfully.")

print("=" * 60)


# ============================================================
# Allowed file types
# ============================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf"
}


# ============================================================
# Detection cleanup
# ============================================================

def remove_detection_markers(raw_text):
    """
    Convert Unlimited-OCR output such as:

    <|det|>text [100,100,500,150]<|/det|>Hello

    into:

    Hello

    Image blocks are ignored.
    """

    if not raw_text:
        return ""

    lines = raw_text.splitlines()

    cleaned_blocks = []

    current_block = None

    detection_pattern = re.compile(
        r"<\|det\|>"
        r"([^<\s]+)"
        r"(?:\s*\[[^\]]*\])?"
        r"\s*"
        r"<\|/det\|>"
        r"(.*)"
    )

    for line in lines:

        line = line.rstrip()

        if not line.strip():
            continue

        match = detection_pattern.match(line)

        if match:

            category = match.group(1).strip()

            content = match.group(2).strip()

            # Ignore image detection blocks
            if category == "image":

                if current_block:
                    cleaned_blocks.append(
                        current_block
                    )

                    current_block = None

                continue


            # Save previous block
            if current_block is not None:

                cleaned_blocks.append(
                    current_block
                )


            current_block = []

            if content:

                current_block.append(
                    content
                )

            continue


        # Normal continuation line
        if current_block is None:

            current_block = []

        current_block.append(line)


    # Save last block
    if current_block is not None:

        cleaned_blocks.append(
            current_block
        )


    result = "\n\n".join(

        "\n".join(block)

        for block in cleaned_blocks

        if block

    ).strip()


    return result


# ============================================================
# Read saved OCR result
# ============================================================

def read_saved_result(output_dir):
    """
    Unlimited-OCR saves its inference result when
    save_results=True.

    Search recursively for text/markdown output.
    """

    if not os.path.exists(output_dir):

        return ""


    candidates = []


    for root, _, files in os.walk(
        output_dir
    ):

        for filename in files:

            lower_name = filename.lower()

            if lower_name.endswith(
                (
                    ".txt",
                    ".md"
                )
            ):

                candidates.append(
                    os.path.join(
                        root,
                        filename
                    )
                )


    # Prefer markdown files
    candidates.sort(
        key=lambda path: (
            0
            if path.lower().endswith(".md")
            else 1,
            path
        )
    )


    for file_path in candidates:

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read().strip()


            if content:

                return content


        except (
            OSError,
            UnicodeDecodeError
        ):

            continue


    return ""


# ============================================================
# Single image OCR
# ============================================================

def process_image(
    image_path,
    output_dir
):
    """
    Official Unlimited-OCR single-image
    Transformers inference.

    Uses the documented Gundam configuration.
    """

    os.makedirs(
        output_dir,
        exist_ok=True
    )


    print(
        "\nRunning single-image OCR..."
    )

    print(
        "Image:",
        image_path
    )


    result = model.infer(

        tokenizer,

        prompt="<image>document parsing.",

        image_file=image_path,

        output_path=output_dir,

        # Official single-image Gundam configuration
        base_size=1024,

        image_size=640,

        crop_mode=True,

        max_length=32768,

        no_repeat_ngram_size=35,

        ngram_window=128,

        save_results=True
    )


    # infer() normally saves results and may return None
    raw_text = read_saved_result(
        output_dir
    )


    # Fallback if infer returns text
    if (
        not raw_text
        and isinstance(result, str)
    ):

        raw_text = result


    cleaned_text = (
        remove_detection_markers(
            raw_text
        )
    )


    return {
        "rawText": raw_text,
        "text": cleaned_text
    }


# ============================================================
# Convert PDF to images
# ============================================================

def pdf_to_images(
    pdf_path,
    dpi=300
):
    """
    Convert PDF pages to PNG images.

    Official Unlimited-OCR PDF example uses
    300 DPI before infer_multi().
    """

    document = fitz.open(
        pdf_path
    )


    temp_dir = tempfile.mkdtemp(
        prefix="unlimited_ocr_pdf_"
    )


    image_paths = []


    try:

        matrix = fitz.Matrix(
            dpi / 72,
            dpi / 72
        )


        for page_number, page in enumerate(
            document
        ):

            output_path = os.path.join(

                temp_dir,

                f"page_{page_number + 1:04d}.png"

            )


            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )


            pixmap.save(
                output_path
            )


            image_paths.append(
                output_path
            )


    finally:

        document.close()


    return (
        image_paths,
        temp_dir
    )


# ============================================================
# Multi-page / PDF OCR
# ============================================================

def process_pdf(
    pdf_path,
    output_dir
):
    """
    Official Unlimited-OCR multi-page inference.

    PDF:
        PDF
         ↓
        300 DPI PNG pages
         ↓
        model.infer_multi()
    """

    os.makedirs(
        output_dir,
        exist_ok=True
    )


    print(
        "\nConverting PDF pages..."
    )


    page_images = []

    temp_dir = None


    try:

        page_images, temp_dir = pdf_to_images(
            pdf_path,
            dpi=300
        )


        if not page_images:

            raise RuntimeError(
                "PDF contains no pages."
            )


        print(
            f"PDF contains {len(page_images)} page(s)."
        )


        print(
            "\nRunning multi-page Unlimited-OCR..."
        )


        # ====================================================
        # IMPORTANT:
        #
        # PDF / multi-page uses infer_multi()
        #
        # Official configuration:
        #
        # image_size=1024
        # ngram_window=1024
        # ====================================================

        result = model.infer_multi(

            tokenizer,

            prompt="<image>Multi page parsing.",

            image_files=page_images,

            output_path=output_dir,

            image_size=1024,

            max_length=32768,

            no_repeat_ngram_size=35,

            ngram_window=1024,

            save_results=True
        )


        # infer_multi() may return None because
        # results are saved to output_path
        raw_text = read_saved_result(
            output_dir
        )


        # Fallback if result itself is text
        if (
            not raw_text
            and isinstance(result, str)
        ):

            raw_text = result


        cleaned_text = (
            remove_detection_markers(
                raw_text
            )
        )


        return {
            "rawText": raw_text,
            "text": cleaned_text,
            "pageCount": len(page_images)
        }


    finally:

        # Clean temporary PDF page images
        if (
            temp_dir
            and os.path.exists(temp_dir)
        ):

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def home():

    return jsonify({

        "success": True,

        "message":
            "Unlimited-OCR API is running",

        "model":
            MODEL_NAME,

        "gpu":
            GPU_NAME,

        "vram":
            round(
                GPU_MEMORY,
                2
            ),

        "supportedFiles": [

            "jpg",
            "jpeg",
            "png",
            "webp",
            "pdf"

        ]

    })


# ============================================================
# Health endpoint
# ============================================================

@app.get("/health")
def health():

    return jsonify({

        "success": True,

        "cuda":
            torch.cuda.is_available(),

        "model":
            MODEL_NAME,

        "gpu":
            GPU_NAME,

        "vram":
            round(
                GPU_MEMORY,
                2
            )

    })


# ============================================================
# OCR endpoint
# ============================================================

@app.post("/ocr")
def perform_ocr():

    uploaded_path = None

    request_id = str(
        uuid.uuid4()
    )


    request_output_dir = os.path.join(

        OUTPUT_DIR,

        request_id

    )


    try:

        # ====================================================
        # Validate uploaded file
        # ====================================================

        if "image" not in request.files:

            return jsonify({

                "success": False,

                "message":
                    "No file uploaded. "
                    "Use form-data field 'image'."

            }), 400


        uploaded_file = request.files[
            "image"
        ]


        if not uploaded_file.filename:

            return jsonify({

                "success": False,

                "message":
                    "No file selected."

            }), 400


        original_filename = (
            uploaded_file.filename
        )


        extension = os.path.splitext(

            original_filename

        )[1].lower()


        if extension not in ALLOWED_EXTENSIONS:

            return jsonify({

                "success": False,

                "message":
                    "Unsupported file type.",

                "supportedFiles": [
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                    "pdf"
                ]

            }), 400


        # ====================================================
        # Create request output directory
        # ====================================================

        os.makedirs(

            request_output_dir,

            exist_ok=True

        )


        # ====================================================
        # Save uploaded file
        # ====================================================

        uploaded_path = os.path.join(

            UPLOAD_DIR,

            f"{request_id}{extension}"

        )


        uploaded_file.save(
            uploaded_path
        )


        print("\n")
        print("=" * 60)

        print(
            "New OCR request"
        )

        print(
            "File:",
            original_filename
        )

        print(
            "Type:",
            extension
        )

        print(
            "Request ID:",
            request_id
        )

        print("=" * 60)


        # ====================================================
        # PDF
        # ====================================================

        if extension == ".pdf":

            result = process_pdf(

                uploaded_path,

                request_output_dir

            )


            print(
                "\nPDF OCR completed."
            )


            print(
                "Pages:",
                result["pageCount"]
            )


            print(
                "=" * 60
            )


            return jsonify({

                "success": True,

                "message":
                    "PDF OCR completed successfully.",

                "type":
                    "pdf",

                "model":
                    MODEL_NAME,

                "pageCount":
                    result["pageCount"],

                "text":
                    result["text"],

                "rawText":
                    result["rawText"],

                "requestId":
                    request_id

            }), 200


        # ====================================================
        # IMAGE
        # ====================================================

        result = process_image(

            uploaded_path,

            request_output_dir

        )


        print(
            "\nImage OCR completed."
        )


        print(
            "=" * 60
        )


        return jsonify({

            "success": True,

            "message":
                "Image OCR completed successfully.",

            "type":
                "image",

            "model":
                MODEL_NAME,

            "text":
                result["text"],

            "rawText":
                result["rawText"],

            "requestId":
                request_id

        }), 200


    except Exception as error:

        print("\n")
        print("=" * 60)

        print(
            "OCR ERROR"
        )

        print(
            type(error).__name__
        )

        print(
            str(error)
        )

        print("=" * 60)


        return jsonify({

            "success": False,

            "message":
                "OCR processing failed.",

            "error":
                str(error),

            "requestId":
                request_id

        }), 500


    finally:

        # ====================================================
        # Remove original uploaded file
        # ====================================================

        if (
            uploaded_path
            and os.path.exists(
                uploaded_path
            )
        ):

            try:

                os.remove(
                    uploaded_path
                )

            except Exception as cleanup_error:

                print(
                    "Upload cleanup failed:",
                    cleanup_error
                )


# ============================================================
# Start server
# ============================================================

if __name__ == "__main__":

    print("\n")

    print("=" * 60)

    print(
        "Unlimited-OCR API"
    )

    print(
        "http://localhost:8000"
    )

    print("=" * 60)

    print(
        "Supported: JPG, JPEG, PNG, WEBP, PDF"
    )

    print("=" * 60)


    app.run(

        host="0.0.0.0",

        port=8000,

        debug=False

    )