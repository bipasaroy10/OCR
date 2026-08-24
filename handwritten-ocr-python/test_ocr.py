import os
import torch

from transformers import AutoModel, AutoTokenizer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "baidu/Unlimited-OCR"

IMAGE_PATH = "images/handwritten-note.jpeg"

OUTPUT_DIR = "output"


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("Unlimited-OCR Python Test")
print("=" * 70)


# ============================================================
# GPU CHECK
# ============================================================

print("\nChecking PyTorch...")

print("PyTorch:", torch.__version__)

print(
    "CUDA available:",
    torch.cuda.is_available()
)


if not torch.cuda.is_available():

    raise RuntimeError(
        "CUDA is not available. "
        "Please fix CUDA/PyTorch before continuing."
    )


GPU_NAME = torch.cuda.get_device_name(0)

VRAM = (
    torch.cuda.get_device_properties(0).total_memory
    / 1024**3
)


print("GPU:", GPU_NAME)

print(
    "VRAM:",
    round(VRAM, 2),
    "GB"
)


# ============================================================
# CHECK IMAGE
# ============================================================

print("\nChecking image...")

if not os.path.exists(IMAGE_PATH):

    raise FileNotFoundError(
        f"Image not found: {IMAGE_PATH}"
    )


print(
    "Image:",
    IMAGE_PATH
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# LOAD TOKENIZER
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("Tokenizer loaded.")


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading Unlimited-OCR model...")

model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch.bfloat16,
)


model = model.eval().cuda()


print("Unlimited-OCR model loaded successfully.")


# ============================================================
# MODEL INFORMATION
# ============================================================

print("\nModel device:")

print(
    next(model.parameters()).device
)


print("\nModel dtype:")

print(
    next(model.parameters()).dtype
)


# ============================================================
# RUN OCR
# ============================================================

print("\n" + "=" * 70)
print("Running OCR...")
print("=" * 70)

print("\nPlease wait...\n")


result = model.infer(
    tokenizer,

    prompt="<image>document parsing.",

    image_file=IMAGE_PATH,

    output_path=OUTPUT_DIR,

    base_size=1024,

    image_size=640,

    crop_mode=True,

    max_length=32768,

    no_repeat_ngram_size=35,

    ngram_window=128,

    save_results=True,
)


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 70)
print("OCR COMPLETED")
print("=" * 70)

print("\nReturned result:")

print(result)


print("\nOutput directory:")

print(
    os.path.abspath(OUTPUT_DIR)
)


print("\n" + "=" * 70)