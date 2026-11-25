
import os
from pathlib import Path

import pytesseract
from PIL import Image


class OCREngine:
    """Extracts text from images using Tesseract OCR."""

    def __init__(self, tesseract_path: str | None = None):
        configured_path = (
            tesseract_path
            or os.getenv("TESSERACT_CMD")
        )

        if configured_path:
            pytesseract.pytesseract.tesseract_cmd = configured_path

    def extract_text(
        self,
        image_path: str | Path,
        language: str = "spa+eng",
    ) -> str:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError("Image file does not exist.")

        if not image_path.is_file():
            raise ValueError("Image path must point to a file.")

        with Image.open(image_path) as image:
            return pytesseract.image_to_string(
                image,
                lang=language,
            ).strip()
