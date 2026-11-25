
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

from invoiceflow.document import Document, DocumentType
from invoiceflow.extraction.pdf_extractor import PDFTextExtractor
from invoiceflow.ocr.ocr_engine import OCREngine


class DocumentProcessor:
    """Processes digital PDFs, scanned PDFs and images."""

    def __init__(
        self,
        pdf_extractor: PDFTextExtractor | None = None,
        ocr_engine: OCREngine | None = None,
    ):
        self.pdf_extractor = pdf_extractor or PDFTextExtractor()
        self.ocr_engine = ocr_engine or OCREngine()

    def process(self, document: Document) -> str:
        if not isinstance(document, Document):
            raise TypeError("Document must be a Document instance.")

        if document.document_type == DocumentType.IMAGE:
            return self.ocr_engine.extract_text(document.path)

        extracted_text = self.pdf_extractor.extract(document)

        if extracted_text:
            return extracted_text

        return self._extract_scanned_pdf(document.path)

    def _extract_scanned_pdf(self, pdf_path: Path) -> str:
        extracted_pages = []

        with TemporaryDirectory() as temp_dir:
            with pymupdf.open(pdf_path) as pdf:
                for page_number, page in enumerate(pdf):
                    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                    image_path = Path(temp_dir) / f"page_{page_number}.png"
                    pixmap.save(image_path)

                    page_text = self.ocr_engine.extract_text(image_path)
                    extracted_pages.append(page_text)

        return "\n".join(extracted_pages).strip()
