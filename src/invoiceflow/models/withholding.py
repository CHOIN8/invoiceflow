
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class Withholding:
    concept: str
    taxable_base: Decimal
    rate: Decimal
    amount: Decimal

    def __post_init__(self):
        if not isinstance(self.concept, str):
            raise TypeError("Withholding concept must be a string.")

        if not self.concept.strip():
            raise ValueError("Withholding concept cannot be empty.")

        if not isinstance(self.taxable_base, Decimal):
            raise TypeError("Taxable base must be a Decimal.")

        if not isinstance(self.rate, Decimal):
            raise TypeError("Withholding rate must be a Decimal.")

        if not isinstance(self.amount, Decimal):
            raise TypeError("Withholding amount must be a Decimal.")

        if not all(
            value.is_finite()
            for value in (
                self.taxable_base,
                self.rate,
                self.amount,
            )
        ):
            raise ValueError("Withholding values must be finite.")

        if self.taxable_base < Decimal("0"):
            raise ValueError("Taxable base cannot be negative.")

        if self.rate < Decimal("0"):
            raise ValueError("Withholding rate cannot be negative.")

        if self.rate > Decimal("100"):
            raise ValueError("Withholding rate cannot exceed 100%.")

        if self.amount < Decimal("0"):
            raise ValueError("Withholding amount cannot be negative.")

        expected_amount = (
            self.taxable_base * self.rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if self.amount != expected_amount:
            raise ValueError(
                "Withholding amount does not match taxable base and rate."
            )
