
from pathlib import Path

import pytest

from invoiceflow.document import Document, DocumentType


def test_create_pdf_document(tmp_path):
    file_path = tmp_path / "invoice.pdf"
    file_path.write_bytes(b"PDF content")

    document = Document(file_path)

    assert document.path == file_path
    assert document.filename == "invoice.pdf"
    assert document.document_type == DocumentType.PDF


def test_create_image_document(tmp_path):
    file_path = tmp_path / "invoice.png"
    file_path.write_bytes(b"Image content")

    document = Document(file_path)

    assert document.filename == "invoice.png"
    assert document.document_type == DocumentType.IMAGE


@pytest.mark.parametrize(
    "extension",
    [".jpg", ".jpeg", ".tif", ".tiff"],
)
def test_supported_image_extensions(tmp_path, extension):
    file_path = tmp_path / f"invoice{extension}"
    file_path.write_bytes(b"Image content")

    document = Document(file_path)

    assert document.document_type == DocumentType.IMAGE


def test_document_rejects_missing_file(tmp_path):
    file_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        Document(file_path)


def test_document_rejects_unsupported_format(tmp_path):
    file_path = tmp_path / "invoice.txt"
    file_path.write_text("Not an invoice")

    with pytest.raises(ValueError, match="Unsupported document format"):
        Document(file_path)


def test_document_rejects_directory(tmp_path):
    directory = tmp_path / "documents"
    directory.mkdir()

    with pytest.raises(ValueError, match="must point to a file"):
        Document(directory)


def test_document_rejects_invalid_path_type():
    with pytest.raises(TypeError, match="must be a string or Path"):
        Document(123)
