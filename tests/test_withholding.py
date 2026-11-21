
from decimal import Decimal

import pytest

from invoiceflow.models.withholding import Withholding


def test_create_withholding():
    withholding = Withholding(
        concept="IRPF",
        taxable_base=Decimal("1000.00"),
        rate=Decimal("15"),
        amount=Decimal("150.00"),
    )

    assert withholding.concept == "IRPF"
    assert withholding.taxable_base == Decimal("1000.00")
    assert withholding.rate == Decimal("15")
    assert withholding.amount == Decimal("150.00")


def test_reject_empty_concept():
    with pytest.raises(ValueError):
        Withholding(
            concept=" ",
            taxable_base=Decimal("1000.00"),
            rate=Decimal("15"),
            amount=Decimal("150.00"),
        )


def test_reject_negative_taxable_base():
    with pytest.raises(ValueError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("-100"),
            rate=Decimal("15"),
            amount=Decimal("15"),
        )


def test_reject_negative_rate():
    with pytest.raises(ValueError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("100"),
            rate=Decimal("-5"),
            amount=Decimal("5"),
        )


def test_reject_rate_above_100():
    with pytest.raises(ValueError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("100"),
            rate=Decimal("101"),
            amount=Decimal("101"),
        )


def test_reject_negative_amount():
    with pytest.raises(ValueError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("100"),
            rate=Decimal("15"),
            amount=Decimal("-15"),
        )


def test_reject_non_decimal_taxable_base():
    with pytest.raises(TypeError):
        Withholding(
            concept="IRPF",
            taxable_base=100,
            rate=Decimal("15"),
            amount=Decimal("15"),
        )


def test_reject_non_decimal_rate():
    with pytest.raises(TypeError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("100"),
            rate=15,
            amount=Decimal("15"),
        )


def test_reject_non_decimal_amount():
    with pytest.raises(TypeError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("100"),
            rate=Decimal("15"),
            amount=15,
        )

def test_reject_incorrect_withholding_amount():
    with pytest.raises(ValueError):
        Withholding(
            concept="IRPF",
            taxable_base=Decimal("1000.00"),
            rate=Decimal("15"),
            amount=Decimal("140.00"),
        )

def test_withholding_rounds_amount_to_two_decimal_places():
    withholding = Withholding(
        concept="IRPF",
        taxable_base=Decimal("100.05"),
        rate=Decimal("15"),
        amount=Decimal("15.01"),
    )

    assert withholding.amount == Decimal("15.01")
@pytest.mark.parametrize(
    "field, value",
    [
        ("taxable_base", Decimal("NaN")),
        ("taxable_base", Decimal("Infinity")),
        ("rate", Decimal("NaN")),
        ("rate", Decimal("Infinity")),
        ("amount", Decimal("NaN")),
        ("amount", Decimal("Infinity")),
    ],
)
def test_withholding_rejects_non_finite_values(field, value):
    values = {
        "concept": "IRPF",
        "taxable_base": Decimal("1000.00"),
        "rate": Decimal("15"),
        "amount": Decimal("150.00"),
    }
    values[field] = value

    with pytest.raises(
        ValueError,
        match="Withholding values must be finite",
    ):
        Withholding(**values)
