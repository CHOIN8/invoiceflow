
import pymupdf

from invoiceflow.document import Document, DocumentType


class PDFTextExtractor:
    """Extracts text from digital PDF documents."""

    def extract(self, document: Document) -> str:
        if not isinstance(document, Document):
            raise TypeError("Document must be a Document instance.")

        if document.document_type != DocumentType.PDF:
            raise ValueError("Document must be a PDF.")

        extracted_pages = []

        with pymupdf.open(document.path) as pdf:
            for page in pdf:
                extracted_pages.append(page.get_text())

        return "\n".join(extracted_pages).strip()

    def has_extractable_text(self, document: Document) -> bool:
        return bool(self.extract(document).strip())

    def needs_ocr(self, document: Document) -> bool:
        return not self.has_extractable_text(document)
