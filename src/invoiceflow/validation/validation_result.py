
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def requires_review(self) -> bool:
        return bool(self.errors or self.warnings)

    def add_error(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("Error message must be a string.")

        if not message.strip():
            raise ValueError("Error message cannot be empty.")

        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("Warning message must be a string.")

        if not message.strip():
            raise ValueError("Warning message cannot be empty.")

        self.warnings.append(message)
