
from decimal import Decimal
from datetime import date, datetime

import pytest

from invoiceflow.confidence import ConfidenceLevel
from invoiceflow.extracted_data import ExtractedInvoiceData
from invoiceflow.models.tax_breakdown import TaxBreakdown


def test_create_extracted_data_with_empty_fields():
    data = ExtractedInvoiceData()

    assert data.invoice_number is None
    assert data.issue_date is None
    assert data.supplier_name is None
    assert data.supplier_tax_id is None
    assert data.taxable_base is None
    assert data.vat_amount is None
    assert data.total_amount is None


def test_create_extracted_data_with_values():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 22),
        supplier_name="Proveedor S.L.",
        supplier_tax_id="B12345678",
        taxable_base=Decimal("100.00"),
        vat_amount=Decimal("21.00"),
        total_amount=Decimal("121.00"),
    )

    assert data.invoice_number == "INV-001"
    assert data.issue_date == date(2026, 11, 22)
    assert data.supplier_name == "Proveedor S.L."
    assert data.supplier_tax_id == "B12345678"
    assert data.taxable_base == Decimal("100.00")
    assert data.vat_amount == Decimal("21.00")
    assert data.total_amount == Decimal("121.00")

def test_reject_invalid_string_field():
    with pytest.raises(TypeError, match="invoice_number"):
        ExtractedInvoiceData(invoice_number=123)


def test_reject_invalid_issue_date():
    with pytest.raises(TypeError, match="Issue date"):
        ExtractedInvoiceData(issue_date="2026-11-22")


def test_reject_invalid_decimal_type():
    with pytest.raises(TypeError, match="taxable_base"):
        ExtractedInvoiceData(taxable_base=100.00)


def test_reject_non_finite_decimal():
    with pytest.raises(ValueError, match="finite"):
        ExtractedInvoiceData(taxable_base=Decimal("NaN"))


def test_reject_negative_taxable_base():
    with pytest.raises(ValueError, match="negative"):
        ExtractedInvoiceData(taxable_base=Decimal("-10.00"))


def test_reject_negative_vat_amount():
    with pytest.raises(ValueError, match="negative"):
        ExtractedInvoiceData(vat_amount=Decimal("-2.00"))


def test_reject_negative_total_amount():
    with pytest.raises(ValueError, match="negative"):
        ExtractedInvoiceData(total_amount=Decimal("-12.00"))
def test_reject_datetime_as_issue_date():
    with pytest.raises(TypeError, match="Issue date"):
        ExtractedInvoiceData(
            issue_date=datetime(2026, 11, 22, 10, 30)
        )

def test_field_without_confidence_requires_review():
    data = ExtractedInvoiceData(invoice_number="INV-001")

    assert data.field_requires_review("invoice_number") is True


def test_field_with_high_confidence_does_not_require_review():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        confidence={"invoice_number": ConfidenceLevel.HIGH},
    )

    assert data.field_requires_review("invoice_number") is False


def test_field_with_medium_confidence_requires_review():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        confidence={"invoice_number": ConfidenceLevel.MEDIUM},
    )

    assert data.field_requires_review("invoice_number") is True


def test_field_with_low_confidence_requires_review():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        confidence={"invoice_number": ConfidenceLevel.LOW},
    )

    assert data.field_requires_review("invoice_number") is True


def test_unknown_field_requires_review():
    data = ExtractedInvoiceData()

    assert data.field_requires_review("unknown_field") is True


def test_reject_invalid_confidence_type():
    with pytest.raises(TypeError, match="Confidence must be a dictionary"):
        ExtractedInvoiceData(confidence="high")


def test_reject_unknown_confidence_field():
    with pytest.raises(ValueError, match="Unknown confidence field"):
        ExtractedInvoiceData(confidence={"unknown_field": ConfidenceLevel.HIGH})


def test_reject_invalid_confidence_level():
    with pytest.raises(TypeError, match="must be a ConfidenceLevel"):
        ExtractedInvoiceData(confidence={"invoice_number": "high"})
def test_requires_review_when_required_field_is_missing():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        confidence={"invoice_number": ConfidenceLevel.HIGH},
    )

    assert data.requires_review is True


def test_requires_review_when_confidence_is_missing():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 22),
        supplier_name="Proveedor S.L.",
        supplier_tax_id="B12345678",
        taxable_base=Decimal("100.00"),
        vat_amount=Decimal("21.00"),
        total_amount=Decimal("121.00"),
        confidence={
            "invoice_number": ConfidenceLevel.HIGH,
            "issue_date": ConfidenceLevel.HIGH,
            "supplier_name": ConfidenceLevel.HIGH,
            "supplier_tax_id": ConfidenceLevel.HIGH,
            "taxable_base": ConfidenceLevel.HIGH,
            "vat_amount": ConfidenceLevel.HIGH,
        },
    )

    assert data.requires_review is True


def test_requires_review_when_one_field_has_low_confidence():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 22),
        supplier_name="Proveedor S.L.",
        supplier_tax_id="B12345678",
        taxable_base=Decimal("100.00"),
        vat_amount=Decimal("21.00"),
        total_amount=Decimal("121.00"),
        confidence={
            "invoice_number": ConfidenceLevel.HIGH,
            "issue_date": ConfidenceLevel.HIGH,
            "supplier_name": ConfidenceLevel.LOW,
            "supplier_tax_id": ConfidenceLevel.HIGH,
            "taxable_base": ConfidenceLevel.HIGH,
            "vat_amount": ConfidenceLevel.HIGH,
            "total_amount": ConfidenceLevel.HIGH,
        },
    )

    assert data.requires_review is True


def test_requires_review_returns_false_when_all_fields_are_valid():
    data = ExtractedInvoiceData(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 22),
        supplier_name="Proveedor S.L.",
        supplier_tax_id="B12345678",
        taxable_base=Decimal("100.00"),
        vat_amount=Decimal("21.00"),
        total_amount=Decimal("121.00"),
        confidence={
            "invoice_number": ConfidenceLevel.HIGH,
            "issue_date": ConfidenceLevel.HIGH,
            "supplier_name": ConfidenceLevel.HIGH,
            "supplier_tax_id": ConfidenceLevel.HIGH,
            "taxable_base": ConfidenceLevel.HIGH,
            "vat_amount": ConfidenceLevel.HIGH,
            "total_amount": ConfidenceLevel.HIGH,
        },
    )

    assert data.requires_review is False

def test_create_extracted_data_with_tax_breakdowns():
    breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        ),
        TaxBreakdown(
            taxable_base=Decimal("500.00"),
            tax_rate=Decimal("10"),
            tax_amount=Decimal("50.00"),
        ),
    ]

    data = ExtractedInvoiceData(tax_breakdowns=breakdowns)

    assert data.tax_breakdowns == breakdowns
    assert len(data.tax_breakdowns) == 2


def test_extracted_data_has_empty_tax_breakdowns_by_default():
    data = ExtractedInvoiceData()

    assert data.tax_breakdowns == []


def test_reject_invalid_tax_breakdowns_type():
    with pytest.raises(TypeError, match="tax_breakdowns"):
        ExtractedInvoiceData(tax_breakdowns="invalid")
def test_reject_tax_breakdowns_with_inconsistent_taxable_base():
    breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    with pytest.raises(ValueError, match="taxable base"):
        ExtractedInvoiceData(
            taxable_base=Decimal("1200.00"),
            tax_breakdowns=breakdowns,
        )


def test_reject_tax_breakdowns_with_inconsistent_vat_amount():
    breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    with pytest.raises(ValueError, match="VAT amount"):
        ExtractedInvoiceData(
            vat_amount=Decimal("200.00"),
            tax_breakdowns=breakdowns,
        )
def test_inconsistent_invoice_total_requires_review():
    breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    data = ExtractedInvoiceData(
        invoice_number="INV-500",
        issue_date=date(2026, 11, 22),
        supplier_name="Proveedor S.L.",
        supplier_tax_id="B12345678",
        taxable_base=Decimal("1000.00"),
        vat_amount=Decimal("210.00"),
        total_amount=Decimal("1300.00"),
        tax_breakdowns=breakdowns,
        confidence={
            "invoice_number": ConfidenceLevel.HIGH,
            "issue_date": ConfidenceLevel.HIGH,
            "supplier_name": ConfidenceLevel.HIGH,
            "supplier_tax_id": ConfidenceLevel.HIGH,
            "taxable_base": ConfidenceLevel.HIGH,
            "vat_amount": ConfidenceLevel.HIGH,
            "total_amount": ConfidenceLevel.HIGH,
        },
    )

    assert data.total_matches_components is False
    assert data.requires_review is True


def test_accept_consistent_invoice_total_with_tax_breakdowns():
    breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    data = ExtractedInvoiceData(
        taxable_base=Decimal("1000.00"),
        vat_amount=Decimal("210.00"),
        total_amount=Decimal("1210.00"),
        tax_breakdowns=breakdowns,
    )

    assert data.total_amount == Decimal("1210.00")