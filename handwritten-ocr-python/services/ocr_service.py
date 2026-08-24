import os
import re
import shutil
import tempfile
from pathlib import Path

import fitz
import torch

from transformers import (
    AutoModel,
    AutoTokenizer
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "baidu/Unlimited-OCR"

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# OCR SERVICE
# ============================================================

class OCRService:

    def __init__(self):

        print("=" * 70)
        print("Loading Unlimited-OCR")
        print("=" * 70)

        # ----------------------------------------------------
        # Check PyTorch
        # ----------------------------------------------------

        print(
            "PyTorch:",
            torch.__version__
        )


        # ----------------------------------------------------
        # Check CUDA
        # ----------------------------------------------------

        cuda_available = (
            torch.cuda.is_available()
        )


        print(
            "CUDA:",
            cuda_available
        )


        if not cuda_available:

            raise RuntimeError(
                "CUDA is not available. "
                "Unlimited-OCR requires a CUDA GPU."
            )


        # ----------------------------------------------------
        # GPU information
        # ----------------------------------------------------

        gpu_name = (
            torch.cuda.get_device_name(0)
        )


        gpu_memory = (
            torch.cuda
            .get_device_properties(0)
            .total_memory
            / 1024**3
        )


        print(
            "GPU:",
            gpu_name
        )


        print(
            "VRAM:",
            round(
                gpu_memory,
                2
            ),
            "GB"
        )


        # ----------------------------------------------------
        # Tokenizer
        # ----------------------------------------------------

        print(
            "\nLoading tokenizer..."
        )


        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                MODEL_NAME,
                trust_remote_code=True
            )
        )


        print(
            "Tokenizer loaded."
        )


        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        print(
            "\nLoading Unlimited-OCR model..."
        )


        self.model = (
            AutoModel.from_pretrained(
                MODEL_NAME,
                trust_remote_code=True,
                use_safetensors=True,
                torch_dtype=torch.bfloat16
            )
        )


        # ----------------------------------------------------
        # Move model to GPU
        # ----------------------------------------------------

        self.model = (
            self.model
            .eval()
            .cuda()
        )


        print(
            "Unlimited-OCR loaded successfully."
        )


        print(
            "Device:",
            next(
                self.model.parameters()
            ).device
        )


        print(
            "Dtype:",
            next(
                self.model.parameters()
            ).dtype
        )


        print("=" * 70)


    # ========================================================
    # CLEAN OCR TEXT
    # ========================================================

    def clean_text(
        self,
        text: str
    ) -> str:

        if not text:

            return ""


        # ----------------------------------------------------
        # Remove detection tags
        # ----------------------------------------------------

        text = re.sub(
            r"<\|det\|>",
            "",
            text
        )


        text = re.sub(
            r"<\|/det\|>",
            "",
            text
        )


        # ----------------------------------------------------
        # Remove bounding boxes
        # ----------------------------------------------------

        text = re.sub(
            r"\[\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\]",
            "",
            text
        )


        # ----------------------------------------------------
        # Remove excessive blank lines
        # ----------------------------------------------------

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )


        return text.strip()


    # ========================================================
    # RESULT FILE
    # ========================================================

    def _result_file(
        self
    ) -> Path:

        return (
            OUTPUT_DIR /
            "result.md"
        )


    # ========================================================
    # REMOVE OLD RESULT
    # ========================================================

    def _remove_old_result(
        self
    ):

        result_file = (
            self._result_file()
        )


        if result_file.exists():

            result_file.unlink()


    # ========================================================
    # READ RESULT
    # ========================================================

    def read_result_file(
        self
    ) -> str:

        result_file = (
            self._result_file()
        )


        if not result_file.exists():

            raise RuntimeError(
                "OCR completed but "
                "result.md was not generated."
            )


        text = result_file.read_text(
            encoding="utf-8"
        )


        return self.clean_text(
            text
        )


    # ========================================================
    # IMAGE OCR
    # ========================================================

    def extract_image_text(
        self,
        image_path: str
    ) -> str:

        if not os.path.exists(
            image_path
        ):

            raise FileNotFoundError(
                f"Image not found: "
                f"{image_path}"
            )


        print(
            "\nRunning IMAGE OCR..."
        )


        self._remove_old_result()


        # ----------------------------------------------------
        # Run Unlimited-OCR
        # ----------------------------------------------------

        self.model.infer(

            self.tokenizer,

            prompt=(
                "<image>"
                "document parsing."
            ),

            image_file=image_path,

            output_path=str(
                OUTPUT_DIR
            ),

            base_size=1024,

            image_size=640,

            crop_mode=True,

            max_length=32768,

            no_repeat_ngram_size=35,

            ngram_window=128,

            save_results=True
        )


        print(
            "Image OCR completed."
        )


        return self.read_result_file()


    # ========================================================
    # PDF → IMAGES
    # ========================================================

    def pdf_to_images(
        self,
        pdf_path: str,
        dpi: int = 300
    ):

        if not os.path.exists(
            pdf_path
        ):

            raise FileNotFoundError(
                f"PDF not found: "
                f"{pdf_path}"
            )


        print(
            "\nConverting PDF pages to images..."
        )


        doc = fitz.open(
            pdf_path
        )


        temp_dir = tempfile.mkdtemp(
            prefix="ocr_pdf_"
        )


        image_paths = []


        try:

            matrix = fitz.Matrix(
                dpi / 72,
                dpi / 72
            )


            for index, page in enumerate(
                doc
            ):

                image_path = os.path.join(
                    temp_dir,
                    f"page_{index + 1:04d}.png"
                )


                page.get_pixmap(
                    matrix=matrix
                ).save(
                    image_path
                )


                image_paths.append(
                    image_path
                )


            print(
                "PDF converted successfully:",
                len(image_paths),
                "pages"
            )


            return (
                temp_dir,
                image_paths
            )


        finally:

            doc.close()


    # ========================================================
    # PDF OCR
    # ========================================================

    def extract_pdf_text(
        self,
        pdf_path: str
    ):

        if not os.path.exists(
            pdf_path
        ):

            raise FileNotFoundError(
                f"PDF not found: "
                f"{pdf_path}"
            )


        print(
            "\nRunning PDF OCR..."
        )


        temp_dir = None


        self._remove_old_result()


        try:

            # ------------------------------------------------
            # Convert PDF to images
            # ------------------------------------------------

            (
                temp_dir,
                image_paths
            ) = self.pdf_to_images(
                pdf_path,
                dpi=300
            )


            if not image_paths:

                raise RuntimeError(
                    "PDF contains no pages."
                )


            # ------------------------------------------------
            # Multi-page OCR
            # ------------------------------------------------

            print(
                f"\nSending "
                f"{len(image_paths)} "
                f"pages to Unlimited-OCR..."
            )


            self.model.infer_multi(

                self.tokenizer,

                prompt=(
                    "<image>"
                    "Multi page parsing."
                ),

                image_files=image_paths,

                output_path=str(
                    OUTPUT_DIR
                ),

                image_size=1024,

                max_length=32768,

                no_repeat_ngram_size=35,

                ngram_window=1024,

                save_results=True
            )


            print(
                "\nPDF OCR completed."
            )


            text = (
                self.read_result_file()
            )


            return {

                "text": text,

                "page_count": len(
                    image_paths
                )
            }


        finally:

            # ------------------------------------------------
            # Remove temporary images
            # ------------------------------------------------

            if (
                temp_dir
                and
                os.path.exists(
                    temp_dir
                )
            ):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )


                print(
                    "Temporary PDF images removed."
                )


    # ========================================================
    # UNIVERSAL OCR
    # ========================================================

    def extract_text(
        self,
        file_path: str
    ):

        if not os.path.exists(
            file_path
        ):

            raise FileNotFoundError(
                f"File not found: "
                f"{file_path}"
            )


        extension = (
            Path(file_path)
            .suffix
            .lower()
        )


        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if extension == ".pdf":

            return self.extract_pdf_text(
                file_path
            )


        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        supported_images = {

            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".bmp"
        }


        if extension in supported_images:

            text = (
                self.extract_image_text(
                    file_path
                )
            )


            return {

                "text": text,

                "page_count": 1
            }


        # ----------------------------------------------------
        # Unsupported
        # ----------------------------------------------------

        raise ValueError(
            f"Unsupported file type: "
            f"{extension}"
        )