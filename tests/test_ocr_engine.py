
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import pytest

from invoiceflow.ocr.ocr_engine import OCREngine


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def create_test_image(path: Path):
    image = Image.new("RGB", (1200, 250), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 60)

    draw.text(
        (50, 70),
        "INVOICE 12345",
        fill="black",
        font=font,
    )

    image.save(path)


def test_extract_text_from_image(tmp_path):
    file_path = tmp_path / "invoice.png"
    create_test_image(file_path)

    engine = OCREngine(tesseract_path=TESSERACT_PATH)

    result = engine.extract_text(file_path, language="eng")

    assert "INVOICE" in result
    assert "12345" in result


def test_extract_text_rejects_missing_file(tmp_path):
    engine = OCREngine(tesseract_path=TESSERACT_PATH)

    with pytest.raises(FileNotFoundError, match="does not exist"):
        engine.extract_text(tmp_path / "missing.png")


def test_extract_text_rejects_directory(tmp_path):
    engine = OCREngine(tesseract_path=TESSERACT_PATH)

    with pytest.raises(ValueError, match="must point to a file"):
        engine.extract_text(tmp_path)
