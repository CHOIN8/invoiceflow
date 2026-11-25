
from datetime import date
from decimal import Decimal

import pytest

from invoiceflow.confidence import ConfidenceLevel
from invoiceflow.extracted_data import ExtractedInvoiceData
from invoiceflow.extraction.invoice_extractor import InvoiceExtractor
from invoiceflow.models.tax_breakdown import TaxBreakdown


INVOICE_TEXT = """
DISTRIBUCIONES FICTICIAS DE PRUEBA
PROBERO PROBANDO HERNANDEZ
NIF/CIF: X0000000T

CLIENTE
PRUEBASED GARCIA PROBERO
NIF: 77777777B

FECHA Nº FACTURA PÁGINA
24-11-2012 98765 1

Base imponible
1.026,00 21 215,46

TOTAL FACTURA
1.026,00 215,46 1.241,46

FORMA DE PAGO: CONTADO
"""


def test_extracts_invoice_data():
    extractor = InvoiceExtractor()

    result = extractor.extract(INVOICE_TEXT)

    assert isinstance(result, ExtractedInvoiceData)
    assert result.supplier_name == "DISTRIBUCIONES FICTICIAS DE PRUEBA"
    assert result.supplier_tax_id == "X0000000T"
    assert result.invoice_number == "98765"
    assert result.issue_date == date(2012, 11, 24)
    assert result.taxable_base == Decimal("1026.00")
    assert result.vat_amount == Decimal("215.46")
    assert result.total_amount == Decimal("1241.46")


def test_extracted_fields_have_confidence():
    extractor = InvoiceExtractor()

    result = extractor.extract(INVOICE_TEXT)

    assert result.confidence["supplier_name"] == ConfidenceLevel.MEDIUM
    assert result.confidence["supplier_tax_id"] == ConfidenceLevel.HIGH
    assert result.confidence["invoice_number"] == ConfidenceLevel.HIGH
    assert result.confidence["issue_date"] == ConfidenceLevel.HIGH
    assert result.confidence["total_amount"] == ConfidenceLevel.HIGH


def test_extract_rejects_non_string_text():
    extractor = InvoiceExtractor()

    with pytest.raises(TypeError):
        extractor.extract(123)


def test_extract_rejects_empty_text():
    extractor = InvoiceExtractor()

    with pytest.raises(ValueError):
        extractor.extract("   ")


def test_does_not_extract_client_tax_id_as_supplier_tax_id():
    extractor = InvoiceExtractor()

    text_without_supplier_tax_id = INVOICE_TEXT.replace(
        "NIF/CIF: X0000000T",
        "",
    ).replace(
        "NIF: 77777777B",
        "NIF/CIF: 77777777B",
    )

    result = extractor.extract(text_without_supplier_tax_id)

    assert result.supplier_tax_id is None
    assert result.supplier_name is None


@pytest.mark.parametrize(
    ("vat_rate", "vat_amount", "total_amount"),
    [
        ("10", "102,60", "1.128,60"),
        ("4", "41,04", "1.067,04"),
    ],
)
def test_extracts_different_vat_rates(
    vat_rate,
    vat_amount,
    total_amount,
):
    extractor = InvoiceExtractor()

    text = INVOICE_TEXT.replace(
        "1.026,00 21 215,46",
        f"1.026,00 {vat_rate} {vat_amount}",
    ).replace(
        "1.026,00 215,46 1.241,46",
        f"1.026,00 {vat_amount} {total_amount}",
    )

    result = extractor.extract(text)

    assert result.taxable_base == Decimal("1026.00")
    assert result.vat_amount == Decimal(vat_amount.replace(",", "."))
    assert result.total_amount == Decimal(
        total_amount.replace(".", "").replace(",", ".")
    )
def test_extracts_multiple_tax_breakdowns():
    extractor = InvoiceExtractor()

    text = INVOICE_TEXT.replace(
        "1.026,00 21 215,46",
        (
            "1.000,00 21 210,00\n"
            "500,00 10 50,00\n"
            "200,00 4 8,00"
        ),
    ).replace(
        "1.026,00 215,46 1.241,46",
        "1.700,00 268,00 1.968,00",
    )

    result = extractor.extract(text)

    assert result.tax_breakdowns == [
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
        TaxBreakdown(
            taxable_base=Decimal("200.00"),
            tax_rate=Decimal("4"),
            tax_amount=Decimal("8.00"),
        ),
    ]

    assert result.taxable_base == Decimal("1700.00")
    assert result.vat_amount == Decimal("268.00")
    assert result.total_amount == Decimal("1968.00")


def test_extractor_marks_invoice_for_review_when_total_is_inconsistent():
    extractor = InvoiceExtractor()

    inconsistent_text = INVOICE_TEXT.replace(
        "1.026,00 215,46 1.241,46",
        "1.026,00 215,46 1.300,00",
    )

    result = extractor.extract(inconsistent_text)

    assert result.total_amount == Decimal("1300.00")
    assert result.confidence["total_amount"] == ConfidenceLevel.MEDIUM
    assert result.total_matches_components is False
    assert result.requires_review is True
