
import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from invoiceflow.models.invoice import Invoice, InvoiceType
from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.models.withholding import Withholding
from invoiceflow.models.adjustment import (
    Adjustment,
    AdjustmentType,
    AdjustmentTaxTreatment,
)
from invoiceflow.models.payment import Payment


CSV_FIELDS = [
    "id",
    "invoice_number",
    "issue_date",
    "supplier_name",
    "supplier_tax_id",
    "tax_breakdown",
    "withholdings",
    "adjustments",
    "payments",
    "due_date",
    "currency",
    "document_total",
    "invoice_type",
    "original_invoice_number",
    "original_invoice_id",
    "rectification_reason",
]


def _serialize_list(items):
    """Serialize nested invoice data as JSON."""
    return json.dumps(items, ensure_ascii=False)


def _invoice_to_row(invoice: Invoice) -> dict:
    """Convert an Invoice into a CSV-compatible row."""

    return {
        "id": str(invoice.id),
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date.isoformat(),
        "supplier_name": invoice.supplier_name,
        "supplier_tax_id": invoice.supplier_tax_id,
        "tax_breakdown": _serialize_list([
            {
                "taxable_base": str(item.taxable_base),
                "tax_rate": str(item.tax_rate),
                "tax_amount": str(item.tax_amount),
            }
            for item in invoice.tax_breakdown
        ]),
        "withholdings": _serialize_list([
            {
                "concept": item.concept,
                "taxable_base": str(item.taxable_base),
                "rate": str(item.rate),
                "amount": str(item.amount),
            }
            for item in invoice.withholdings
        ]),
        "adjustments": _serialize_list([
            {
                "concept": item.concept,
                "adjustment_type": item.adjustment_type.value,
                "tax_treatment": item.tax_treatment.value,
                "amount": str(item.amount),
                "tax_rate": (
                    str(item.tax_rate)
                    if item.tax_rate is not None
                    else None
                ),
            }
            for item in invoice.adjustments
        ]),
        "payments": _serialize_list([
            {
                "payment_date": item.payment_date.isoformat(),
                "amount": str(item.amount),
                "method": item.method,
                "reference": item.reference,
            }
            for item in invoice.payments
        ]),
        "due_date": (
            invoice.due_date.isoformat()
            if invoice.due_date is not None
            else ""
        ),
        "currency": invoice.currency,
        "document_total": (
            str(invoice.document_total)
            if invoice.document_total is not None
            else ""
        ),
        "invoice_type": invoice.invoice_type.value,
        "original_invoice_number": invoice.original_invoice_number or "",
        "original_invoice_id": (
            str(invoice.original_invoice_id)
            if invoice.original_invoice_id is not None
            else ""
        ),
        "rectification_reason": invoice.rectification_reason or "",
    }


def export_invoices_csv(
    invoices: list[Invoice],
    file_path: str | Path,
) -> None:
    """Export invoices to a CSV file."""

    if not isinstance(invoices, list):
        raise TypeError("Invoices must be provided as a list.")

    if not all(isinstance(invoice, Invoice) for invoice in invoices):
        raise TypeError("All items must be Invoice instances.")

    file_path = Path(file_path)

    with file_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDS,
        )
        writer.writeheader()

        for invoice in invoices:
            writer.writerow(_invoice_to_row(invoice))


def _deserialize_invoice(row: dict) -> Invoice:
    """Rebuild an Invoice from a CSV row."""

    tax_breakdown = [
        TaxBreakdown(
            taxable_base=Decimal(item["taxable_base"]),
            tax_rate=Decimal(item["tax_rate"]),
            tax_amount=Decimal(item["tax_amount"]),
        )
        for item in json.loads(row["tax_breakdown"])
    ]

    withholdings = [
        Withholding(
            concept=item["concept"],
            taxable_base=Decimal(item["taxable_base"]),
            rate=Decimal(item["rate"]),
            amount=Decimal(item["amount"]),
        )
        for item in json.loads(row["withholdings"])
    ]

    adjustments = [
        Adjustment(
            concept=item["concept"],
            adjustment_type=AdjustmentType(item["adjustment_type"]),
            tax_treatment=AdjustmentTaxTreatment(
                item["tax_treatment"]
            ),
            amount=Decimal(item["amount"]),
            tax_rate=(
                Decimal(item["tax_rate"])
                if item["tax_rate"] is not None
                else None
            ),
        )
        for item in json.loads(row["adjustments"])
    ]

    payments = [
        Payment(
            payment_date=date.fromisoformat(item["payment_date"]),
            amount=Decimal(item["amount"]),
            method=item["method"],
            reference=item["reference"],
        )
        for item in json.loads(row["payments"])
    ]

    return Invoice(
        id=UUID(row["id"]),
        invoice_number=row["invoice_number"],
        issue_date=date.fromisoformat(row["issue_date"]),
        supplier_name=row["supplier_name"],
        supplier_tax_id=row["supplier_tax_id"],
        tax_breakdown=tax_breakdown,
        withholdings=withholdings,
        adjustments=adjustments,
        payments=payments,
        due_date=(
            date.fromisoformat(row["due_date"])
            if row["due_date"]
            else None
        ),
        currency=row["currency"],
        document_total=(
            Decimal(row["document_total"])
            if row["document_total"]
            else None
        ),
        invoice_type=InvoiceType(row["invoice_type"]),
        original_invoice_number=(
            row["original_invoice_number"] or None
        ),
        original_invoice_id=(
            UUID(row["original_invoice_id"])
            if row["original_invoice_id"]
            else None
        ),
        rectification_reason=row["rectification_reason"] or None,
    )


def import_invoices_csv(
    file_path: str | Path,
) -> list[Invoice]:
    """Import invoices from a CSV file."""

    file_path = Path(file_path)

    invoices = []

    with file_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames != CSV_FIELDS:
            raise ValueError("CSV file has an invalid InvoiceFlow format.")

        for row_number, row in enumerate(reader, start=2):
            try:
                invoices.append(_deserialize_invoice(row))
            except (KeyError, TypeError, ValueError, ArithmeticError) as error:
                raise ValueError(
                    f"Invalid invoice data on CSV row {row_number}: {error}"
                ) from error

    return invoices
