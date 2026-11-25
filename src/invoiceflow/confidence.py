
from enum import Enum


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def requires_review(self) -> bool:
        return self != ConfidenceLevel.HIGH
