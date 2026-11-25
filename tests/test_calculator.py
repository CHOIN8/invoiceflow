from datetime import date
from decimal import Decimal

import pytest

from invoiceflow.calculator import InvoiceCalculator


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (Decimal("10.124"), Decimal("10.12")),
        (Decimal("10.125"), Decimal("10.13")),
        (Decimal("10.126"), Decimal("10.13")),
        (Decimal("99.995"), Decimal("100.00")),
        (Decimal("0"), Decimal("0.00")),
    ],
)
def test_round_amount(amount, expected):
    result = InvoiceCalculator.round_amount(amount)

    assert result == expected
@pytest.mark.parametrize(
    ("taxable_base", "tax_rate", "expected"),
    [
        (Decimal("1000"), Decimal("21"), Decimal("210.00")),
        (Decimal("1000"), Decimal("10"), Decimal("100.00")),
        (Decimal("1000"), Decimal("4"), Decimal("40.00")),
        (Decimal("99.99"), Decimal("21"), Decimal("21.00")),
    ],
)
def test_calculate_tax(taxable_base, tax_rate, expected):
    result = InvoiceCalculator.calculate_tax(taxable_base, tax_rate)

    assert result == expected
@pytest.mark.parametrize(
    ("taxable_base", "rate", "expected"),
    [
        (Decimal("1000"), Decimal("15"), Decimal("150.00")),
        (Decimal("1000"), Decimal("7"), Decimal("70.00")),
        (Decimal("500"), Decimal("2"), Decimal("10.00")),
        (Decimal("99.99"), Decimal("15"), Decimal("15.00")),
    ],
)
def test_calculate_withholding(taxable_base, rate, expected):
    result = InvoiceCalculator.calculate_withholding(taxable_base, rate)

    assert result == expected
from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.models.withholding import Withholding


def test_calculate_total_with_vat_and_withholding():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    withholdings = [
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("1000.00"),
            rate=Decimal("15"),
            amount=Decimal("150.00"),
        )
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        withholdings,
    )

    assert result == Decimal("1060.00")

def test_calculate_total_with_multiple_vat_rates():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("21.00"),
        ),
        TaxBreakdown(
            taxable_base=Decimal("200.00"),
            tax_rate=Decimal("10"),
            tax_amount=Decimal("20.00"),
        ),
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("4"),
            tax_amount=Decimal("4.00"),
        ),
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        [],
    )

    assert result == Decimal("445.00")
def test_calculate_total_without_withholdings():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        [],
    )

    assert result == Decimal("1210.00")
@pytest.mark.parametrize(
    "amount",
    [
        10,
        10.5,
        "10.50",
        None,
    ],
)
def test_round_amount_rejects_non_decimal(amount):
    with pytest.raises(TypeError, match="must be a Decimal"):
        InvoiceCalculator.round_amount(amount)


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_round_amount_rejects_non_finite_values(amount):
    with pytest.raises(ValueError, match="must be finite"):
        InvoiceCalculator.round_amount(amount)
@pytest.mark.parametrize(
    ("taxable_base", "tax_rate", "error"),
    [
        (Decimal("-100"), Decimal("21"), ValueError),
        (Decimal("100"), Decimal("-21"), ValueError),
        (Decimal("100"), Decimal("101"), ValueError),
        (Decimal("NaN"), Decimal("21"), ValueError),
        (100, Decimal("21"), TypeError),
        (Decimal("100"), 21, TypeError),
    ],
)
def test_calculate_tax_rejects_invalid_inputs(
    taxable_base,
    tax_rate,
    error,
):
    with pytest.raises(error):
        InvoiceCalculator.calculate_tax(taxable_base, tax_rate)
@pytest.mark.parametrize(
    ("taxable_base", "rate", "error"),
    [
        (Decimal("-100"), Decimal("15"), ValueError),
        (Decimal("100"), Decimal("-15"), ValueError),
        (Decimal("100"), Decimal("101"), ValueError),
        (Decimal("NaN"), Decimal("15"), ValueError),
        (100, Decimal("15"), TypeError),
        (Decimal("100"), 15, TypeError),
    ],
)
def test_calculate_withholding_rejects_invalid_inputs(
    taxable_base,
    rate,
    error,
):
    with pytest.raises(error):
        InvoiceCalculator.calculate_withholding(taxable_base, rate)
def test_calculate_total_rejects_invalid_tax_breakdowns():
    with pytest.raises(TypeError, match="Tax breakdowns must be a list"):
        InvoiceCalculator.calculate_total(
            "not a list",
            [],
        )
def test_calculate_total_rejects_invalid_tax_breakdown_items():
    with pytest.raises(
        TypeError,
        match="All tax breakdown items must be TaxBreakdown instances",
    ):
        InvoiceCalculator.calculate_total(
            ["invalid item"],
            [],
        )
def test_calculate_total_rejects_invalid_withholdings():
    with pytest.raises(TypeError, match="Withholdings must be a list"):
        InvoiceCalculator.calculate_total(
            [],
            "not a list",
        )
def test_calculate_total_rejects_invalid_withholding_items():
    with pytest.raises(
        TypeError,
        match="All withholding items must be Withholding instances",
    ):
        InvoiceCalculator.calculate_total(
            [],
            ["invalid item"],
        )

from invoiceflow.models.adjustment import (
    Adjustment,
    AdjustmentTaxTreatment,
    AdjustmentType,
)


def test_calculate_total_with_before_tax_discount():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    withholdings = [
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("1000.00"),
            rate=Decimal("15"),
            amount=Decimal("150.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Commercial discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("100.00"),
            tax_rate=Decimal("21"),
        )
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        withholdings,
        adjustments,
    )

    assert result == Decimal("939.00")


def test_calculate_total_with_before_tax_surcharge():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Additional charge",
            adjustment_type=AdjustmentType.SURCHARGE,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("25.00"),
            tax_rate=Decimal("21"),
        )
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        [],
        adjustments,
    )

    assert result == Decimal("1240.25")


def test_calculate_total_with_after_tax_discount():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Final discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
            amount=Decimal("25.00"),
        )
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        [],
        adjustments,
    )

    assert result == Decimal("1185.00")


def test_calculate_total_with_after_tax_surcharge():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Final surcharge",
            adjustment_type=AdjustmentType.SURCHARGE,
            tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
            amount=Decimal("25.00"),
        )
    ]

    result = InvoiceCalculator.calculate_total(
        tax_breakdowns,
        [],
        adjustments,
    )

    assert result == Decimal("1235.00")


def test_reject_discount_exceeding_taxable_base():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("100.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("21.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Excessive discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("150.00"),
            tax_rate=Decimal("21"),
        )
    ]

    with pytest.raises(ValueError, match="exceeds taxable base"):
        InvoiceCalculator.calculate_total(
            tax_breakdowns,
            [],
            adjustments,
        )
    from datetime import date

from invoiceflow.models.payment import Payment


def test_calculate_paid_amount_with_multiple_payments():
    payments = [
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("300.00"),
            method="Bank transfer",
        ),
        Payment(
            payment_date=date(2026, 11, 21),
            amount=Decimal("200.00"),
            method="Card",
        ),
    ]

    result = InvoiceCalculator.calculate_paid_amount(payments)

    assert result == Decimal("500.00")


def test_calculate_paid_amount_without_payments():
    result = InvoiceCalculator.calculate_paid_amount([])

    assert result == Decimal("0.00")


def test_calculate_balance_with_partial_payment():
    payments = [
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("300.00"),
        )
    ]

    result = InvoiceCalculator.calculate_balance(
        Decimal("1000.00"),
        payments,
    )

    assert result == Decimal("700.00")


def test_calculate_balance_with_full_payment():
    payments = [
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("1000.00"),
        )
    ]

    result = InvoiceCalculator.calculate_balance(
        Decimal("1000.00"),
        payments,
    )

    assert result == Decimal("0.00")


def test_calculate_balance_with_overpayment():
    payments = [
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("1200.00"),
        )
    ]

    result = InvoiceCalculator.calculate_balance(
        Decimal("1000.00"),
        payments,
    )

    assert result == Decimal("-200.00")
@pytest.mark.parametrize(
    "payments",
    [
        "not a list",
        None,
        123,
    ],
)
def test_calculate_paid_amount_rejects_invalid_list(payments):
    with pytest.raises(TypeError, match="Payments must be a list"):
        InvoiceCalculator.calculate_paid_amount(payments)


def test_calculate_paid_amount_rejects_invalid_items():
    with pytest.raises(
        TypeError,
        match="All payment items must be Payment instances",
    ):
        InvoiceCalculator.calculate_paid_amount(["invalid"])


@pytest.mark.parametrize(
    "invoice_total",
    [
        100,
        "100.00",
        None,
    ],
)
def test_calculate_balance_rejects_non_decimal_total(invoice_total):
    with pytest.raises(TypeError, match="must be a Decimal"):
        InvoiceCalculator.calculate_balance(invoice_total, [])


@pytest.mark.parametrize(
    "invoice_total",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_calculate_balance_rejects_non_finite_total(invoice_total):
    with pytest.raises(ValueError, match="must be finite"):
        InvoiceCalculator.calculate_balance(invoice_total, [])


def test_calculate_balance_rejects_negative_invoice_total():
    with pytest.raises(ValueError, match="cannot be negative"):
        InvoiceCalculator.calculate_balance(Decimal("-10.00"), [])

def test_calculate_adjusted_taxable_base_without_adjustments():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    result = InvoiceCalculator.calculate_adjusted_taxable_base(
        tax_breakdowns
    )

    assert result == Decimal("1000.00")


def test_calculate_adjusted_taxable_base_with_discount():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Commercial discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("100.00"),
            tax_rate=Decimal("21"),
        )
    ]

    result = InvoiceCalculator.calculate_adjusted_taxable_base(
        tax_breakdowns,
        adjustments,
    )

    assert result == Decimal("900.00")


def test_calculate_adjusted_taxable_base_with_surcharge():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Additional charge",
            adjustment_type=AdjustmentType.SURCHARGE,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("50.00"),
            tax_rate=Decimal("21"),
        )
    ]

    result = InvoiceCalculator.calculate_adjusted_taxable_base(
        tax_breakdowns,
        adjustments,
    )

    assert result == Decimal("1050.00")


def test_calculate_adjusted_taxable_base_ignores_after_tax_discount():
    tax_breakdowns = [
        TaxBreakdown(
            taxable_base=Decimal("1000.00"),
            tax_rate=Decimal("21"),
            tax_amount=Decimal("210.00"),
        )
    ]

    adjustments = [
        Adjustment(
            concept="Final discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
            amount=Decimal("100.00"),
        )
    ]

    result = InvoiceCalculator.calculate_adjusted_taxable_base(
        tax_breakdowns,
        adjustments,
    )

    assert result == Decimal("1000.00")
