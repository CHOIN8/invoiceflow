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