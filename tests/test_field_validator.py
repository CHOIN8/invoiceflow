
from datetime import date
from decimal import Decimal

import pytest

from invoiceflow.confidence import ConfidenceLevel
from invoiceflow.extracted_data import ExtractedInvoiceData
from invoiceflow.validation.field_validator import validate_extracted_data


def create_valid_extracted_data():
    return ExtractedInvoiceData(
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


def test_validate_extracted_data_with_valid_data():
    data = create_valid_extracted_data()

    result = validate_extracted_data(data)

    assert result.is_valid is True
    assert result.requires_review is False
    assert result.errors == []
    assert result.warnings == []


def test_validate_extracted_data_with_missing_field():
    data = create_valid_extracted_data()
    data.invoice_number = None

    result = validate_extracted_data(data)

    assert result.is_valid is False
    assert result.requires_review is True
    assert len(result.errors) == 1
    assert "invoice_number" in result.errors[0]


def test_validate_extracted_data_with_low_confidence():
    data = create_valid_extracted_data()
    data.confidence["supplier_name"] = ConfidenceLevel.LOW

    result = validate_extracted_data(data)

    assert result.is_valid is True
    assert result.requires_review is True
    assert result.errors == []
    assert len(result.warnings) == 1
    assert "supplier_name" in result.warnings[0]


def test_validate_extracted_data_with_missing_confidence():
    data = create_valid_extracted_data()
    del data.confidence["vat_amount"]

    result = validate_extracted_data(data)

    assert result.is_valid is True
    assert result.requires_review is True
    assert len(result.warnings) == 1
    assert "vat_amount" in result.warnings[0]


def test_validate_extracted_data_rejects_invalid_type():
    with pytest.raises(TypeError, match="ExtractedInvoiceData"):
        validate_extracted_data("invalid data")
def test_validate_extracted_data_with_inconsistent_total():
    data = create_valid_extracted_data()
    data.total_amount = Decimal("130.00")

    result = validate_extracted_data(data)

    assert result.is_valid is True
    assert result.requires_review is True
    assert result.errors == []
    assert len(result.warnings) == 1
    assert "Invoice total does not match" in result.warnings[0]