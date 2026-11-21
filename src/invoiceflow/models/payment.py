
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Payment:
    payment_date: date
    amount: Decimal
    method: str = ""
    reference: str = ""

    def __post_init__(self):
        if not isinstance(self.payment_date, date):
            raise TypeError("Payment date must be a date.")

        if not isinstance(self.amount, Decimal):
            raise TypeError("Payment amount must be a Decimal.")

        if not self.amount.is_finite():
            raise ValueError("Payment amount must be finite.")

        if self.amount <= Decimal("0"):
            raise ValueError("Payment amount must be greater than zero.")

        if not isinstance(self.method, str):
            raise TypeError("Payment method must be a string.")

        if not isinstance(self.reference, str):
            raise TypeError("Payment reference must be a string.")
