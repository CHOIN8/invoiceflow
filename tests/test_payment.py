
from datetime import date
from decimal import Decimal

import pytest

from invoiceflow.models.payment import Payment


def test_create_payment():
    payment = Payment(
        payment_date=date(2026, 11, 20),
        amount=Decimal("500.00"),
        method="Bank transfer",
        reference="TRF-001",
    )

    assert payment.payment_date == date(2026, 11, 20)
    assert payment.amount == Decimal("500.00")
    assert payment.method == "Bank transfer"
    assert payment.reference == "TRF-001"


def test_create_payment_without_optional_fields():
    payment = Payment(
        payment_date=date(2026, 11, 20),
        amount=Decimal("100.00"),
    )

    assert payment.method == ""
    assert payment.reference == ""


def test_reject_invalid_payment_date():
    with pytest.raises(TypeError):
        Payment(
            payment_date="2026-11-20",
            amount=Decimal("100.00"),
        )


def test_reject_non_decimal_amount():
    with pytest.raises(TypeError):
        Payment(
            payment_date=date(2026, 11, 20),
            amount=100,
        )


def test_reject_zero_amount():
    with pytest.raises(ValueError):
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("0"),
        )


def test_reject_negative_amount():
    with pytest.raises(ValueError):
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("-100"),
        )


def test_reject_non_string_method():
    with pytest.raises(TypeError):
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("100"),
            method=123,
        )


def test_reject_non_string_reference():
    with pytest.raises(TypeError):
        Payment(
            payment_date=date(2026, 11, 20),
            amount=Decimal("100"),
            reference=123,
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
        match="Payment amount must be finite",
    ):
        Payment(
            payment_date=date(2026, 11, 20),
            amount=amount,
        )
