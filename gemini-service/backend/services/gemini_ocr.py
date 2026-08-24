import os

from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def extract_handwritten_text(
    image_bytes: bytes,
    mime_type: str
) -> str:

    prompt = """
You are an OCR system specialized in handwritten documents.

Read the handwritten text in the provided image.

Instructions:

1. Extract only the text that is actually visible.
2. Preserve the original wording as accurately as possible.
3. Preserve paragraphs and line breaks where possible.
4. Preserve numbers, dates, symbols, and punctuation.
5. Do not summarize the content.
6. Do not explain the image.
7. Do not add information that is not present.
8. If a word is unclear, make the best possible interpretation.
9. Return ONLY the extracted text.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),
            prompt
        ]
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned empty text"
        )

    return response.text.strip()