import os
import torch
from transformers import AutoModel, AutoTokenizer


MODEL_NAME = "baidu/Unlimited-OCR"

IMAGE_PATH = "images/handwritten-note.jpeg"

OUTPUT_DIR = "output"


print("=" * 60)
print("Unlimited-OCR Handwritten Note Test")
print("=" * 60)

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available.")

print("GPU:", torch.cuda.get_device_name(0))

vram = (
    torch.cuda.get_device_properties(0).total_memory
    / 1024**3
)

print(f"VRAM: {vram:.2f} GB")


# --------------------------------------------------
# Check image
# --------------------------------------------------

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(
        f"Image not found: {IMAGE_PATH}"
    )

print("\nImage:", IMAGE_PATH)


# --------------------------------------------------
# Create output directory
# --------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------
# Load tokenizer
# --------------------------------------------------

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("Tokenizer loaded.")


# --------------------------------------------------
# Load model
# --------------------------------------------------

print("\nLoading Unlimited-OCR model...")

model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch.bfloat16
)

model = model.eval().cuda()

print("Unlimited-OCR model loaded.")


# --------------------------------------------------
# Run official Unlimited-OCR inference
# --------------------------------------------------

print("\nRunning OCR...")
print("Please wait...")

result = model.infer(
    tokenizer,
    prompt="<image>document parsing.",
    image_file=IMAGE_PATH,
    output_path=OUTPUT_DIR,

    # Official Gundam configuration
    base_size=1024,
    image_size=640,
    crop_mode=True,

    max_length=32768,

    no_repeat_ngram_size=35,
    ngram_window=128,

    save_results=True,
)


# --------------------------------------------------
# Result
# --------------------------------------------------

print("\n")
print("=" * 60)
print("OCR COMPLETED")
print("=" * 60)

print(result)

print("\nOutput directory:")
print(os.path.abspath(OUTPUT_DIR))

print("=" * 60)