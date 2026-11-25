
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DocumentType(Enum):
    PDF = "pdf"
    IMAGE = "image"


@dataclass(frozen=True)
class Document:
    path: Path

    SUPPORTED_PDF_EXTENSIONS = {".pdf"}
    SUPPORTED_IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
    }

    def __post_init__(self):
        if not isinstance(self.path, (str, Path)):
            raise TypeError("Document path must be a string or Path.")

        object.__setattr__(self, "path", Path(self.path))

        if not self.path.exists():
            raise FileNotFoundError("Document file does not exist.")

        if not self.path.is_file():
            raise ValueError("Document path must point to a file.")

        if self.path.suffix.lower() not in (
            self.SUPPORTED_PDF_EXTENSIONS
            | self.SUPPORTED_IMAGE_EXTENSIONS
        ):
            raise ValueError("Unsupported document format.")

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def document_type(self) -> DocumentType:
        if self.path.suffix.lower() in self.SUPPORTED_PDF_EXTENSIONS:
            return DocumentType.PDF

        return DocumentType.IMAGE
