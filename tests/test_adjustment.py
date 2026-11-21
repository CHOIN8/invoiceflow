
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
    )

    assert adjustment.concept == "Commercial discount"
    assert adjustment.adjustment_type == AdjustmentType.DISCOUNT
    assert adjustment.tax_treatment == AdjustmentTaxTreatment.BEFORE_TAX
    assert adjustment.amount == Decimal("100.00")


def test_create_surcharge():
    adjustment = Adjustment(
        concept="Additional charges",
        adjustment_type=AdjustmentType.SURCHARGE,
        tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
        amount=Decimal("25.00"),
    )

    assert adjustment.adjustment_type == AdjustmentType.SURCHARGE
    assert adjustment.tax_treatment == AdjustmentTaxTreatment.AFTER_TAX


def test_reject_empty_concept():
    with pytest.raises(ValueError):
        Adjustment(
            concept=" ",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
        )


def test_reject_non_string_concept():
    with pytest.raises(TypeError):
        Adjustment(
            concept=123,
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
        )


def test_reject_invalid_adjustment_type():
    with pytest.raises(TypeError):
        Adjustment(
            concept="Discount",
            adjustment_type="discount",
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("10.00"),
        )


def test_reject_invalid_tax_treatment():
    with pytest.raises(TypeError):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment="before_tax",
            amount=Decimal("10.00"),
        )


def test_reject_non_decimal_amount():
    with pytest.raises(TypeError):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=10,
        )


def test_reject_negative_amount():
    with pytest.raises(ValueError):
        Adjustment(
            concept="Discount",
            adjustment_type=AdjustmentType.DISCOUNT,
            tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
            amount=Decimal("-10.00"),
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
        )
