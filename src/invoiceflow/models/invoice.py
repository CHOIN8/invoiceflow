from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from invoiceflow.models.adjustment import Adjustment
from invoiceflow.models.payment import Payment
from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.models.withholding import Withholding
from invoiceflow.calculator import InvoiceCalculator



class InvoiceType(Enum):
    STANDARD = "standard"
    RECTIFYING = "rectifying"


@dataclass
class Invoice:
    invoice_number: str
    issue_date: date
    supplier_name: str
    supplier_tax_id: str
    tax_breakdown: list[TaxBreakdown] = field(default_factory=list)
    withholdings: list[Withholding] = field(default_factory=list)
    adjustments: list[Adjustment] = field(default_factory=list)
    payments: list[Payment] = field(default_factory=list)
    due_date: date | None = None
    currency: str = "EUR"
    document_total: Decimal | None = None
    invoice_type: InvoiceType = InvoiceType.STANDARD
    original_invoice_number: str | None = None
    original_invoice_id: UUID | None = None
    rectification_reason: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            raise TypeError("Invoice ID must be a UUID.")
        if (
            self.original_invoice_id is not None
            and not isinstance(self.original_invoice_id, UUID)
        ):
            raise TypeError("Original invoice ID must be a UUID or None.")
        if not isinstance(self.invoice_type, InvoiceType):
            raise TypeError("Invoice type must be an InvoiceType.")

        if self.original_invoice_number is not None:
            if not isinstance(self.original_invoice_number, str):
                raise TypeError("Original invoice number must be a string.")

            if not self.original_invoice_number.strip():
                raise ValueError("Original invoice number cannot be empty.")

        if self.rectification_reason is not None:
            if not isinstance(self.rectification_reason, str):
                raise TypeError("Rectification reason must be a string.")

            if not self.rectification_reason.strip():
                raise ValueError("Rectification reason cannot be empty.")

        if self.invoice_type == InvoiceType.RECTIFYING:
            if self.original_invoice_id == self.id:
                raise ValueError("An invoice cannot rectify itself.")
            if self.original_invoice_number is None:
                raise ValueError("Rectifying invoices must reference an original invoice.")

            if self.original_invoice_id is None:
                raise ValueError(
                    "Rectifying invoices must reference an original invoice ID."
                )

            if self.rectification_reason is None:
                raise ValueError("Rectifying invoices must include a reason.")

        if self.invoice_type == InvoiceType.STANDARD:
            if (
                self.original_invoice_number is not None
                or self.original_invoice_id is not None
                or self.rectification_reason is not None
            ):
                raise ValueError(
                    "Standard invoices cannot contain rectification data."
                )
        if not isinstance(self.tax_breakdown, list):
            raise TypeError("Tax breakdown must be a list.")
        if not all(isinstance(item, TaxBreakdown) for item in self.tax_breakdown):
            raise TypeError("All tax breakdown items must be TaxBreakdown instances.")

        if not isinstance(self.withholdings, list):
            raise TypeError("Withholdings must be a list.")
        if not all(isinstance(item, Withholding) for item in self.withholdings):
            raise TypeError("All withholding items must be Withholding instances.")

        if not isinstance(self.adjustments, list):
            raise TypeError("Adjustments must be a list.")
        if not all(isinstance(item, Adjustment) for item in self.adjustments):
            raise TypeError("All adjustment items must be Adjustment instances.")

        if not isinstance(self.payments, list):
            raise TypeError("Payments must be a list.")
        if not all(isinstance(item, Payment) for item in self.payments):
            raise TypeError("All payment items must be Payment instances.")

        if not isinstance(self.issue_date, date) or isinstance(self.issue_date, datetime):
            raise TypeError("Issue date must be a date.")

        if self.due_date is not None and (
            not isinstance(self.due_date, date)
            or isinstance(self.due_date, datetime)
        ):
            raise TypeError("Due date must be a date.")

        if not isinstance(self.invoice_number, str):
            raise TypeError("Invoice number must be a string.")

        if not self.invoice_number.strip():
            raise ValueError("Invoice number cannot be empty.")
        self.invoice_number = self.invoice_number.strip()

        if not isinstance(self.supplier_name, str):
            raise TypeError("Supplier name must be a string.")

        if not self.supplier_name.strip():
            raise ValueError("Supplier name cannot be empty.")

        self.supplier_name = self.supplier_name.strip()

        if not isinstance(self.supplier_tax_id, str):
            raise TypeError("Supplier tax ID must be a string.")

        if not self.supplier_tax_id.strip():
            raise ValueError("Supplier tax ID cannot be empty.")

        self.supplier_tax_id = self.supplier_tax_id.strip()

        if self.due_date is not None and self.due_date < self.issue_date:
            raise ValueError("Due date cannot be earlier than issue date.")

        if self.document_total is not None:
            if not isinstance(self.document_total, Decimal):
                raise TypeError("Document total must be a Decimal or None.")
            if not self.document_total.is_finite():
                raise ValueError("Document total must be finite.")

            if (
                self.invoice_type == InvoiceType.STANDARD
                and self.document_total < Decimal("0")
            ):
                raise ValueError("Standard invoice total cannot be negative.")

        if not isinstance(self.currency, str):
            raise TypeError("Currency must be a string.")

        if not self.currency.strip():
            raise ValueError("Currency cannot be empty.")
        if (
            len(self.currency) != 3
            or not self.currency.isalpha()
            or self.currency != self.currency.upper()
        ):
            raise ValueError(
                "Currency must be a three-letter uppercase code."
            )

    @property
    def calculated_total(self) -> Decimal:
        return InvoiceCalculator.calculate_total(
            self.tax_breakdown,
            self.withholdings,
            self.adjustments,
        )

    @property
    def paid_amount(self) -> Decimal:
        return InvoiceCalculator.calculate_paid_amount(self.payments)

    @property
    def outstanding_balance(self) -> Decimal:
        return InvoiceCalculator.calculate_balance(
            self.calculated_total,
            self.payments,
        )

    @property
    def document_total_matches_calculated(self) -> bool | None:
        if self.document_total is None:
            return None

        return self.document_total == self.calculated_total