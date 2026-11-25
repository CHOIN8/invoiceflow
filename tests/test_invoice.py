from datetime import date,datetime
from decimal import Decimal

import pytest
from uuid import uuid4

from invoiceflow.models.invoice import Invoice, InvoiceType
from invoiceflow.models.tax_breakdown import TaxBreakdown


def test_create_tax_breakdown():
    tax = TaxBreakdown(
        taxable_base=Decimal("100.00"),
        tax_rate=Decimal("21"),
        tax_amount=Decimal("21.00"),
    )

    assert tax.taxable_base == Decimal("100.00")
    assert tax.tax_rate == Decimal("21")
    assert tax.tax_amount == Decimal("21.00")


def test_create_invoice():
    invoice = Invoice(
        invoice_number="F-2026-001",
        issue_date=date(2026, 11, 20),
        supplier_name="Comercial Garcia SL",
        supplier_tax_id="B12345678",
    )

    assert invoice.invoice_number == "F-2026-001"
    assert invoice.supplier_name == "Comercial Garcia SL"
    assert invoice.currency == "EUR"
    assert invoice.tax_breakdown == []
    assert invoice.document_total is None


def test_tax_breakdown_rejects_negative_taxable_base():
    with pytest.raises(ValueError):
        TaxBreakdown(
            taxable_base=Decimal("-100.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("21.00"),
        )


def test_tax_breakdown_rejects_negative_tax_amount():
    with pytest.raises(ValueError):
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("-21.00"),
        )


def test_tax_breakdown_rejects_tax_rate_above_100():
    with pytest.raises(ValueError):
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("101"),
            tax_amount=Decimal("101.00"),
        )


def test_invoice_rejects_empty_invoice_number():
    with pytest.raises(ValueError, match="Invoice number cannot be empty"):
        Invoice(
            invoice_number="",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
        )


def test_invoice_rejects_empty_supplier_name():
    with pytest.raises(ValueError, match="Supplier name cannot be empty"):
        Invoice(
            invoice_number="F-2026-001",
            issue_date=date(2026, 11, 20),
            supplier_name="",
            supplier_tax_id="B12345678",
        )
def test_invoice_rejects_empty_supplier_tax_id():
    with pytest.raises(ValueError, match="Supplier tax ID cannot be empty"):
        Invoice(
            invoice_number="F-2026-001",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="",
        )

def test_invoice_rejects_non_string_supplier_name():
    with pytest.raises(TypeError, match="Supplier name must be a string"):
        Invoice(
            invoice_number="F-2026-004",
            issue_date=date(2026, 11, 20),
            supplier_name=123,
            supplier_tax_id="B12345678",
        )


def test_invoice_rejects_due_date_before_issue_date():
    with pytest.raises(ValueError, match="Due date cannot be earlier than issue date"):
        Invoice(
            invoice_number="F-2026-001",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            due_date=date(2026, 11, 19),
        )


def test_invoice_rejects_negative_document_total():
    with pytest.raises(
        ValueError,
        match="Standard invoice total cannot be negative",
    ):
        Invoice(
            invoice_number="F-2026-001",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            document_total=Decimal("-50.00"),
        )

def test_tax_breakdown_accepts_zero_tax_rate():
    tax = TaxBreakdown(
        taxable_base=Decimal("100.00"),
        tax_rate=Decimal("0"),
        tax_amount=Decimal("0.00"),
    )

    assert tax.tax_rate == Decimal("0")

def test_invoice_accepts_multiple_tax_breakdowns():
    invoice = Invoice(
        invoice_number="F-2026-002",
        issue_date=date(2026, 11, 20),
        supplier_name="Comercial Garcia SL",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("100.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("21.00"),
            ),
            TaxBreakdown(
                taxable_base=Decimal("50.00"),
                tax_rate=Decimal("10"),
                tax_amount=Decimal("5.00"),
            ),
        ],
    )

    assert len(invoice.tax_breakdown) == 2
    assert invoice.tax_breakdown[0].tax_rate == Decimal("21")
    assert invoice.tax_breakdown[1].tax_rate == Decimal("10")


def test_invoice_rejects_invalid_issue_date():
    with pytest.raises(TypeError):
        Invoice(
            invoice_number="F-2026-003",
            issue_date="20/11/2026",
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
        )


def test_invoice_rejects_non_string_invoice_number():
    with pytest.raises(TypeError, match="Invoice number must be a string"):
        Invoice(
            invoice_number=12345,
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
        )
def test_invoice_rejects_non_string_supplier_tax_id():
    with pytest.raises(TypeError, match="Supplier tax ID must be a string"):
        Invoice(
            invoice_number="F-2026-005",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id=12345678,
        )
def test_invoice_uses_eur_as_default_currency():
    invoice = Invoice(
        invoice_number="F-2026-006",
        issue_date=date(2026, 11, 20),
        supplier_name="Comercial Garcia SL",
        supplier_tax_id="B12345678",
    )

    assert invoice.currency == "EUR"
def test_invoice_rejects_empty_currency():
    with pytest.raises(ValueError, match="Currency cannot be empty"):
        Invoice(
            invoice_number="F-2026-007",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            currency="",
        )
def test_invoice_rejects_non_string_currency():
    with pytest.raises(TypeError, match="Currency must be a string"):
        Invoice(
            invoice_number="F-2026-008",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            currency=123,
        )

def test_invoice_rejects_non_list_tax_breakdown():
    with pytest.raises(TypeError, match="Tax breakdown must be a list"):
        Invoice(
            invoice_number="F-2026-010",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            tax_breakdown="21% VAT",
        )

def test_invoice_rejects_non_decimal_document_total():
    with pytest.raises(TypeError, match="Document total must be a Decimal or None"):
        Invoice(
            invoice_number="F-2026-009",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            document_total=100.50,
        )

def test_invoice_rejects_invalid_tax_breakdown_items():
    with pytest.raises(
        TypeError,
        match="All tax breakdown items must be TaxBreakdown instances",
    ):
        Invoice(
            invoice_number="F-2026-011",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            tax_breakdown=["21% VAT"],
        )
def test_invoice_accepts_empty_tax_breakdown():
    invoice = Invoice(
        invoice_number="F-2026-012",
        issue_date=date(2026, 11, 20),
        supplier_name="Comercial Garcia SL",
        supplier_tax_id="B12345678",
        tax_breakdown=[],
    )

    assert invoice.tax_breakdown == []


def test_invoice_document_total_defaults_to_none():
    invoice = Invoice(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
    )

    assert invoice.document_total is None


def test_invoice_accepts_document_total():
    invoice = Invoice(
        invoice_number="INV-002",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        document_total=Decimal("1210.00"),
    )

    assert invoice.document_total == Decimal("1210.00")


def test_invoice_defaults_to_standard_type():
    invoice = Invoice(
        invoice_number="INV-100",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
    )

    assert invoice.invoice_type == InvoiceType.STANDARD


def test_create_rectifying_invoice():
    invoice = Invoice(
        invoice_number="R-001",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        invoice_type=InvoiceType.RECTIFYING,
        original_invoice_number="INV-100",
        original_invoice_id=uuid4(),
        rectification_reason="Incorrect invoice amount",
    )

    assert invoice.invoice_type is InvoiceType.RECTIFYING
    assert invoice.original_invoice_number == "INV-100"
    assert invoice.rectification_reason == "Incorrect invoice amount"


def test_rectifying_invoice_requires_original_invoice_number():
    with pytest.raises(ValueError, match="must reference an original invoice"):
        Invoice(
            invoice_number="R-002",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type=InvoiceType.RECTIFYING,
            rectification_reason="Incorrect amount",
        )


def test_rectifying_invoice_requires_reason():
    with pytest.raises(ValueError, match="must include a reason"):
        Invoice(
            invoice_number="R-003",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type=InvoiceType.RECTIFYING,
            original_invoice_number="INV-100",
            original_invoice_id=uuid4(),
        )


def test_invoice_rejects_invalid_invoice_type():
    with pytest.raises(TypeError, match="Invoice type must be an InvoiceType"):
        Invoice(
            invoice_number="INV-101",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type="standard",
        )


def test_invoice_rejects_non_string_original_invoice_number():
    with pytest.raises(
        TypeError,
        match="Original invoice number must be a string",
    ):
        Invoice(
            invoice_number="R-004",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type=InvoiceType.RECTIFYING,
            original_invoice_number=12345,
            rectification_reason="Incorrect amount",
        )


def test_invoice_rejects_non_string_rectification_reason():
    with pytest.raises(
        TypeError,
        match="Rectification reason must be a string",
    ):
        Invoice(
            invoice_number="R-005",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type=InvoiceType.RECTIFYING,
            original_invoice_number="INV-100",
            rectification_reason=12345,
        )
def test_invoice_rejects_datetime_as_issue_date():
    with pytest.raises(TypeError, match="Issue date must be a date."):
        Invoice(
            invoice_number="INV-001",
            issue_date=datetime(2026, 1, 15, 10, 30),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
        )
def test_invoice_rejects_invalid_currency_format():
    with pytest.raises(
        ValueError,
        match="Currency must be a three-letter uppercase code",
    ):
        Invoice(
            invoice_number="F-2026-009",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            currency="eur",
        )
def test_invoice_rejects_currency_with_numbers():
    with pytest.raises(
        ValueError,
        match="Currency must be a three-letter uppercase code",
    ):
        Invoice(
            invoice_number="F-2026-010",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            currency="EU1",
        )
def test_invoice_rejects_currency_with_spaces():
    with pytest.raises(
        ValueError,
        match="Currency must be a three-letter uppercase code",
    ):
        Invoice(
            invoice_number="F-2026-011",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            currency="E UR",
        )
def test_invoice_rejects_currency_with_special_characters():
    with pytest.raises(
        ValueError,
        match="Currency must be a three-letter uppercase code",
    ):
        Invoice(
            invoice_number="F-2026-012",
            issue_date=date(2026, 11, 20),
            supplier_name="Comercial Garcia SL",
            supplier_tax_id="B12345678",
            currency="E€R",
        )

def test_tax_breakdown_rejects_non_decimal_taxable_base():
    with pytest.raises(TypeError, match="Taxable base must be a Decimal"):
        TaxBreakdown(
            taxable_base=100,
            tax_rate=Decimal("21"),
            tax_amount=Decimal("21.00"),
        )


def test_tax_breakdown_rejects_non_decimal_tax_rate():
    with pytest.raises(TypeError, match="Tax rate must be a Decimal"):
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=21,
            tax_amount=Decimal("21.00"),
        )


def test_tax_breakdown_rejects_non_decimal_tax_amount():
    with pytest.raises(TypeError, match="Tax amount must be a Decimal"):
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("21"),
            tax_amount=21,
        )
@pytest.mark.parametrize(
    "field, value",
    [
        ("taxable_base", Decimal("NaN")),
        ("taxable_base", Decimal("Infinity")),
        ("tax_rate", Decimal("NaN")),
        ("tax_rate", Decimal("Infinity")),
        ("tax_amount", Decimal("NaN")),
        ("tax_amount", Decimal("Infinity")),
    ],
)
def test_tax_breakdown_rejects_non_finite_values(field, value):
    values = {
        "taxable_base": Decimal("100.00"),
        "tax_rate": Decimal("21"),
        "tax_amount": Decimal("21.00"),
    }
    values[field] = value

    with pytest.raises(ValueError, match="Tax values must be finite"):
        TaxBreakdown(**values)
def test_tax_breakdown_rejects_incorrect_tax_amount():
    with pytest.raises(
        ValueError,
        match="Tax amount does not match taxable base and rate",
    ):
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("20.00"),
        )
def test_tax_breakdown_uses_half_up_rounding():
    tax = TaxBreakdown(
        taxable_base=Decimal("1.00"),
        tax_rate=Decimal("12.5"),
        tax_amount=Decimal("0.13"),
    )

    assert tax.tax_amount == Decimal("0.13")
def test_rectifying_invoice_cannot_reference_itself():
    invoice_id = uuid4()

    with pytest.raises(
        ValueError,
        match="An invoice cannot rectify itself",
    ):
        Invoice(
            invoice_number="R-006",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type=InvoiceType.RECTIFYING,
            original_invoice_number="INV-100",
            original_invoice_id=invoice_id,
            rectification_reason="Incorrect amount",
            id=invoice_id,
        )
def test_rectifying_invoice_rejects_invalid_original_invoice_id():
    with pytest.raises(
        TypeError,
        match="Original invoice ID must be a UUID or None",
    ):
        Invoice(
            invoice_number="R-007",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            invoice_type=InvoiceType.RECTIFYING,
            original_invoice_number="INV-100",
            original_invoice_id="not-a-uuid",
            rectification_reason="Incorrect amount",
        )
@pytest.mark.parametrize(
    "document_total",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_invoice_rejects_non_finite_document_total(document_total):
    with pytest.raises(
        ValueError,
        match="Document total must be finite",
    ):
        Invoice(
            invoice_number="INV-200",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            document_total=document_total,
        )
def test_invoice_rejects_datetime_as_due_date():
    with pytest.raises(
        TypeError,
        match="Due date must be a date",
    ):
        Invoice(
            invoice_number="INV-201",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            due_date=datetime(2026, 12, 20, 10, 30),
        )
def test_invoice_rejects_non_list_payments():
    with pytest.raises(TypeError, match="Payments must be a list"):
        Invoice(
            invoice_number="INV-202",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            payments="500",
        )


def test_invoice_rejects_invalid_payment_items():
    with pytest.raises(
        TypeError,
        match="All payment items must be Payment instances",
    ):
        Invoice(
            invoice_number="INV-203",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            payments=["500"],
        )
def test_invoice_rejects_non_list_withholdings():
    with pytest.raises(TypeError, match="Withholdings must be a list"):
        Invoice(
            invoice_number="INV-204",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            withholdings="15%",
        )


def test_invoice_rejects_invalid_withholding_items():
    with pytest.raises(
        TypeError,
        match="All withholding items must be Withholding instances",
    ):
        Invoice(
            invoice_number="INV-205",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            withholdings=["15%"],
        )
def test_invoice_rejects_non_list_adjustments():
    with pytest.raises(TypeError, match="Adjustments must be a list"):
        Invoice(
            invoice_number="INV-206",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            adjustments="Discount",
        )


def test_invoice_rejects_invalid_adjustment_items():
    with pytest.raises(
        TypeError,
        match="All adjustment items must be Adjustment instances",
    ):
        Invoice(
            invoice_number="INV-207",
            issue_date=date(2026, 11, 20),
            supplier_name="Test Supplier",
            supplier_tax_id="B12345678",
            adjustments=["Discount"],
        )
def test_invoice_uses_independent_default_lists():
    invoice1 = Invoice(
        invoice_number="INV-208",
        issue_date=date(2026, 11, 20),
        supplier_name="Supplier One",
        supplier_tax_id="B12345678",
    )

    invoice2 = Invoice(
        invoice_number="INV-209",
        issue_date=date(2026, 11, 20),
        supplier_name="Supplier Two",
        supplier_tax_id="B87654321",
    )

    assert invoice1.tax_breakdown is not invoice2.tax_breakdown
    assert invoice1.withholdings is not invoice2.withholdings
    assert invoice1.adjustments is not invoice2.adjustments
    assert invoice1.payments is not invoice2.payments
from invoiceflow.models.payment import Payment


def test_invoice_calculated_total():
    invoice = Invoice(
        invoice_number="INV-300",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("1000.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("210.00"),
            )
        ],
    )

    assert invoice.calculated_total == Decimal("1210.00")


def test_invoice_paid_amount():
    invoice = Invoice(
        invoice_number="INV-301",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        payments=[
            Payment(
                payment_date=date(2026, 11, 20),
                amount=Decimal("300.00"),
            ),
            Payment(
                payment_date=date(2026, 11, 21),
                amount=Decimal("200.00"),
            ),
        ],
    )

    assert invoice.paid_amount == Decimal("500.00")


def test_invoice_outstanding_balance():
    invoice = Invoice(
        invoice_number="INV-302",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("1000.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("210.00"),
            )
        ],
        payments=[
            Payment(
                payment_date=date(2026, 11, 20),
                amount=Decimal("500.00"),
            )
        ],
    )

    assert invoice.outstanding_balance == Decimal("710.00")
def test_document_total_matches_calculated():
    invoice = Invoice(
        invoice_number="INV-400",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("1000.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("210.00"),
            )
        ],
        document_total=Decimal("1210.00"),
    )

    assert invoice.document_total_matches_calculated is True


def test_document_total_does_not_match_calculated():
    invoice = Invoice(
        invoice_number="INV-401",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("1000.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("210.00"),
            )
        ],
        document_total=Decimal("1200.00"),
    )

    assert invoice.document_total_matches_calculated is False


def test_document_total_matches_calculated_when_missing():
    invoice = Invoice(
        invoice_number="INV-402",
        issue_date=date(2026, 11, 20),
        supplier_name="Test Supplier",
        supplier_tax_id="B12345678",
    )

    assert invoice.document_total_matches_calculated is None