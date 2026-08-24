from services.ocr_service import OCRService


PDF_PATH = "pdfs/handwritten.pdf"


print("=" * 70)
print("PDF OCR TEST")
print("=" * 70)


ocr = OCRService()


result = ocr.extract_text(
    PDF_PATH
)


print("\n" + "=" * 70)
print("PDF OCR RESULT")
print("=" * 70)


print(
    "Pages:",
    result["page_count"]
)


print("\nExtracted Text:\n")


print(
    result["text"]
)


print("\n" + "=" * 70)
print("PDF OCR TEST COMPLETED")
print("=" * 70)