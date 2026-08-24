from services.ocr_processor import process_file


FILE_PATH = "images/handwritten-note.jpeg"


record = process_file(

    file_path=
        FILE_PATH,

    original_name=
        "handwritten-note.jpeg",

    mime_type=
        "image/jpeg"
)


print("=" * 70)

print("COMPLETE OCR PIPELINE")

print("=" * 70)


print("\nMongoDB ID:")

print(
    record["_id"]
)


print("\nFile:")

print(
    record["originalName"]
)


print("\nPages:")

print(
    record["pageCount"]
)


print("\nOCR TEXT:")

print(
    record["ocrText"]
)


print("\n" + "=" * 70)