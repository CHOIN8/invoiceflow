import pymupdf
import pytest

from invoiceflow.document import Document
from invoiceflow.extraction.pdf_extractor import PDFTextExtractor


def create_pdf(path, pages):
    pdf = pymupdf.open()

    for text in pages:
        page = pdf.new_page()
        page.insert_text((72, 72), text)

    pdf.save(path)
    pdf.close()


def test_extract_text_from_pdf(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, ["Invoice number: INV-001"])

    document = Document(file_path)
    extractor = PDFTextExtractor()

    result = extractor.extract(document)

    assert "Invoice number: INV-001" in result


def test_extract_text_from_multiple_pages(tmp_path):
    file_path = tmp_path / "invoice.pdf"

    create_pdf(
        file_path,
        [
            "First page",
            "Second page",
        ],
    )

    document = Document(file_path)
    extractor = PDFTextExtractor()

    result = extractor.extract(document)

    assert "First page" in result
    assert "Second page" in result


def test_extract_text_from_empty_pdf(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, [""])

    document = Document(file_path)
    extractor = PDFTextExtractor()

    result = extractor.extract(document)

    assert result == ""


def test_extractor_rejects_non_pdf_document(tmp_path):
    file_path = tmp_path / "invoice.png"
    file_path.write_bytes(b"Image content")

    document = Document(file_path)
    extractor = PDFTextExtractor()

    with pytest.raises(ValueError, match="must be a PDF"):
        extractor.extract(document)


def test_extractor_rejects_invalid_document():
    extractor = PDFTextExtractor()

    with pytest.raises(TypeError, match="Document instance"):
        extractor.extract("invoice.pdf")
def test_has_extractable_text_returns_true(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, ["Invoice number: INV-001"])

    document = Document(file_path)
    extractor = PDFTextExtractor()

    assert extractor.has_extractable_text(document) is True


def test_has_extractable_text_returns_false(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, [""])

    document = Document(file_path)
    extractor = PDFTextExtractor()

    assert extractor.has_extractable_text(document) is False

def test_needs_ocr_returns_false_for_digital_pdf(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, ["Invoice number: INV-001"])

    document = Document(file_path)
    extractor = PDFTextExtractor()

    assert extractor.needs_ocr(document) is False


def test_needs_ocr_returns_true_for_scanned_pdf(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    create_pdf(file_path, [""])

    document = Document(file_path)
    extractor = PDFTextExtractor()

    assert extractor.needs_ocr(document) is True