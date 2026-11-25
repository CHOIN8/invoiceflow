
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from invoiceflow.confidence import ConfidenceLevel
from invoiceflow.models.tax_breakdown import TaxBreakdown


@dataclass
class ExtractedInvoiceData:
    invoice_number: str | None = None
    issue_date: date | None = None
    supplier_name: str | None = None
    supplier_tax_id: str | None = None
    taxable_base: Decimal | None = None
    vat_amount: Decimal | None = None
    total_amount: Decimal | None = None
    tax_breakdowns: list[TaxBreakdown] = field(default_factory=list)

    confidence: dict[str, ConfidenceLevel] = field(default_factory=dict)

    def __post_init__(self):
        string_fields = {
            "invoice_number": self.invoice_number,
            "supplier_name": self.supplier_name,
            "supplier_tax_id": self.supplier_tax_id,
        }

        for field_name, value in string_fields.items():
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string.")

        if self.issue_date is not None:
            if not isinstance(self.issue_date, date) or isinstance(
                self.issue_date, datetime
            ):
                raise TypeError("Issue date must be a date.")

        decimal_fields = {
            "taxable_base": self.taxable_base,
            "vat_amount": self.vat_amount,
            "total_amount": self.total_amount,
        }

        for field_name, value in decimal_fields.items():
            if value is None:
                continue
            if not isinstance(value, Decimal):
                raise TypeError(f"{field_name} must be a Decimal.")

            if not value.is_finite():
                raise ValueError(f"{field_name} must be finite.")

            if value < Decimal("0"):
                raise ValueError(f"{field_name} cannot be negative.")

        if not isinstance(self.tax_breakdowns, list):
            raise TypeError("tax_breakdowns must be a list.")

        for breakdown in self.tax_breakdowns:
            if not isinstance(breakdown, TaxBreakdown):
                raise TypeError(
                    "Each tax breakdown must be a TaxBreakdown instance."
                )

        if self.tax_breakdowns:
            breakdown_base = sum(
                (item.taxable_base for item in self.tax_breakdowns),
                Decimal("0"),
            )

            breakdown_vat = sum(
                (item.tax_amount for item in self.tax_breakdowns),
                Decimal("0"),
            )

            if (
                self.taxable_base is not None
                and self.taxable_base != breakdown_base
            ):
                raise ValueError(
                    "Tax breakdowns do not match taxable base."
                )

            if (
                self.vat_amount is not None
                and self.vat_amount != breakdown_vat
            ):
                raise ValueError(
                    "Tax breakdowns do not match VAT amount."
                )

        if not isinstance(self.confidence, dict):
            raise TypeError("Confidence must be a dictionary.")

        valid_fields = {
            "invoice_number",
            "issue_date",
            "supplier_name",
            "supplier_tax_id",
            "taxable_base",
            "vat_amount",
            "total_amount",
        }

        for field_name, level in self.confidence.items():
            if field_name not in valid_fields:
                raise ValueError(f"Unknown confidence field: {field_name}.")

            if not isinstance(level, ConfidenceLevel):
                raise TypeError(
                    f"Confidence for {field_name} must be a ConfidenceLevel."
                )
    @property
    def total_matches_components(self) -> bool | None:
        if (
            self.taxable_base is None
            or self.vat_amount is None
            or self.total_amount is None
        ):
            return None

        return self.total_amount == self.taxable_base + self.vat_amount
    def field_requires_review(self, field_name: str) -> bool:
        if field_name not in self.confidence:
            return True

        return self.confidence[field_name].requires_review
    @property
    def requires_review(self) -> bool:
        required_fields = (
            "invoice_number",
            "issue_date",
            "supplier_name",
            "supplier_tax_id",
            "taxable_base",
            "vat_amount",
            "total_amount",
        )

        for field_name in required_fields:
            if getattr(self, field_name) is None:
                return True

            if self.field_requires_review(field_name):
                return True

        return self.total_matches_components is False