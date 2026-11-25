
import pymupdf

import pytest

from invoiceflow.document import Document
from invoiceflow.document_processor import DocumentProcessor


class FakeOCREngine:
    def __init__(self):
        self.processed_images = []

    def extract_text(self, image_path):
        self.processed_images.append(image_path)
        return f"Recognized text {len(self.processed_images)}"


def create_pdf(path, pages):
    pdf = pymupdf.open()

    for text in pages:
        page = pdf.new_page()
        page.insert_text((72, 72), text)

    pdf.save(path)
    pdf.close()


def test_process_digital_pdf(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, ["Invoice INV-001"])

    document = Document(file_path)
    processor = DocumentProcessor()

    result = processor.process(document)

    assert "Invoice INV-001" in result


def test_process_scanned_pdf(tmp_path):
    file_path = tmp_path / "scanned.pdf"
    create_pdf(file_path, [""])

    document = Document(file_path)
    fake_ocr = FakeOCREngine()
    processor = DocumentProcessor(ocr_engine=fake_ocr)

    result = processor.process(document)

    assert "Recognized text 1" in result
    assert len(fake_ocr.processed_images) == 1


def test_process_scanned_pdf_multiple_pages(tmp_path):
    file_path = tmp_path / "scanned.pdf"
    create_pdf(file_path, ["", ""])

    document = Document(file_path)
    fake_ocr = FakeOCREngine()
    processor = DocumentProcessor(ocr_engine=fake_ocr)

    result = processor.process(document)

    assert "Recognized text 1" in result
    assert "Recognized text 2" in result
    assert len(fake_ocr.processed_images) == 2


def test_process_image(tmp_path):
    file_path = tmp_path / "invoice.png"
    file_path.write_bytes(b"Test image")

    document = Document(file_path)
    fake_ocr = FakeOCREngine()
    processor = DocumentProcessor(ocr_engine=fake_ocr)

    result = processor.process(document)

    assert result == "Recognized text 1"
    assert len(fake_ocr.processed_images) == 1


def test_process_rejects_invalid_document():
    processor = DocumentProcessor()

    with pytest.raises(TypeError, match="Document instance"):
        processor.process("invoice.pdf")
