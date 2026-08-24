from services.ocr_service import OCRService


IMAGE_PATH = "images/handwritten-note.jpeg"


print("=" * 70)
print("OCR SERVICE TEST")
print("=" * 70)


ocr = OCRService()


text = ocr.extract_text(
    IMAGE_PATH
)


print("\n" + "=" * 70)
print("EXTRACTED TEXT")
print("=" * 70)

print(text)

print("\n" + "=" * 70)