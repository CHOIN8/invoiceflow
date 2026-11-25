
from datetime import date
from decimal import Decimal

import pytest

from invoiceflow.models.invoice import Invoice
from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.validation.invoice_validator import validate_invoice


def create_invoice(document_total=Decimal("121.00")):
    return Invoice(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("100.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("21.00"),
            )
        ],
        document_total=document_total,
    )


def test_validate_invoice_with_matching_total():
    invoice = create_invoice()

    result = validate_invoice(invoice)

    assert result.is_valid
    assert not result.requires_review
    assert result.errors == []
    assert result.warnings == []


def test_validate_invoice_warns_when_totals_do_not_match():
    invoice = create_invoice(Decimal("120.00"))

    result = validate_invoice(invoice)

    assert result.is_valid
    assert result.requires_review
    assert result.errors == []
    assert len(result.warnings) == 1


def test_validate_invoice_warns_when_document_total_is_missing():
    invoice = create_invoice(None)

    result = validate_invoice(invoice)

    assert result.is_valid
    assert result.requires_review
    assert result.errors == []
    assert len(result.warnings) == 1


def test_validate_invoice_compares_rounded_totals():
    invoice = create_invoice(Decimal("121.004"))

    result = validate_invoice(invoice)

    assert result.is_valid
    assert not result.requires_review
    assert result.warnings == []


def test_validate_invoice_rejects_invalid_object():
    with pytest.raises(
        TypeError,
        match="Invoice must be an Invoice instance",
    ):
        validate_invoice("not an invoice")
from invoiceflow.models.adjustment import (
    Adjustment,
    AdjustmentTaxTreatment,
    AdjustmentType,
)
def test_validate_invoice_captures_calculation_error():
    invoice = create_invoice()

    invoice.adjustments.append(
        Adjustment(
            concept="Excessive discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("150.00"),
            tax_rate=Decimal("21"),
        )
    )

    result = validate_invoice(invoice)

    assert not result.is_valid
    assert result.requires_review
    assert len(result.errors) == 1