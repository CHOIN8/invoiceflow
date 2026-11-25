
from decimal import Decimal

import pytest

from invoiceflow.models.adjustment import (
    Adjustment,
    AdjustmentTaxTreatment,
    AdjustmentType,
)


def test_create_discount():
    adjustment = Adjustment(
        concept="Commercial discount",
        adjustment_type=AdjustmentType.DISCOUNT,
        tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
        amount=Decimal("100.00"),
        tax_rate=Decimal("21"),
    )

    assert adjustment.concept == "Commercial discount"
    assert adjustment.adjustment_type == AdjustmentType.DISCOUNT
    assert adjustment.tax_treatment == AdjustmentTaxTreatment.BEFORE_TAX
    assert adjustment.amount == Decimal("100.00")
    assert adjustment.tax_rate == Decimal("21")


def test_create_surcharge():
    adjustment = Adjustment(
        concept="Additional charges",
        adjustment_type=AdjustmentType.SURCHARGE,
        tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
        amount=Decimal("25.00"),
    )

    assert adjustment.adjustment_type == AdjustmentType.SURCHARGE
    assert adjustment.tax_treatment == AdjustmentTaxTreatment.AFTER_TAX
    assert adjustment.tax_rate is None


def test_reject_empty_concept():
    with pytest.raises(ValueError):
        Adjustment(
            concept=" ",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
            tax_rate=Decimal("21"),
        )


def test_reject_non_string_concept():
    with pytest.raises(TypeError):
        Adjustment(
            concept=123,
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
            tax_rate=Decimal("21"),
        )


def test_reject_invalid_adjustment_type():
    with pytest.raises(TypeError):
        Adjustment(
            concept="Discount",
            adjustment_type="discount",
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
            tax_rate=Decimal("21"),
        )


def test_reject_invalid_tax_treatment():
    with pytest.raises(TypeError):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment="before_tax",
            amount=Decimal("10.00"),
            tax_rate=Decimal("21"),
        )


def test_reject_non_decimal_amount():
    with pytest.raises(TypeError):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=10,
            tax_rate=Decimal("21"),
        )


def test_reject_negative_amount():
    with pytest.raises(ValueError):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("-10.00"),
            tax_rate=Decimal("21"),
        )


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_reject_non_finite_amount(amount):
    with pytest.raises(
        ValueError,
        match="Adjustment amount must be finite",
    ):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=amount,
            tax_rate=Decimal("21"),
        )


def test_reject_before_tax_adjustment_without_tax_rate():
    with pytest.raises(ValueError, match="must include a tax rate"):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
        )


def test_reject_after_tax_adjustment_with_tax_rate():
    with pytest.raises(ValueError, match="cannot include a tax rate"):
        Adjustment(
            concept="Surcharge",
            adjustment_type=AdjustmentType.SURCHARGE,
            tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
            amount=Decimal("10.00"),
            tax_rate=Decimal("21"),
        )


def test_reject_non_decimal_tax_rate():
    with pytest.raises(TypeError, match="tax rate must be a Decimal"):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
            tax_rate=21,
        )


@pytest.mark.parametrize(
    "tax_rate",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_reject_non_finite_tax_rate(tax_rate):
    with pytest.raises(ValueError, match="tax rate must be finite"):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
            tax_rate=tax_rate,
        )


@pytest.mark.parametrize(
    "tax_rate",
    [
        Decimal("-1"),
        Decimal("101"),
    ],
)
def test_reject_tax_rate_out_of_range(tax_rate):
    with pytest.raises(ValueError, match="between 0 and 100"):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
            tax_rate=tax_rate,
        )
