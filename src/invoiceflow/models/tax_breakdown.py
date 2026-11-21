
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class TaxBreakdown:
    taxable_base: Decimal
    tax_rate: Decimal
    tax_amount: Decimal

    def __post_init__(self):
        if not isinstance(self.taxable_base, Decimal):
            raise TypeError("Taxable base must be a Decimal.")

        if not isinstance(self.tax_rate, Decimal):
            raise TypeError("Tax rate must be a Decimal.")

        if not isinstance(self.tax_amount, Decimal):
            raise TypeError("Tax amount must be a Decimal.")

        if not all(
            value.is_finite()
            for value in (
                self.taxable_base,
                self.tax_rate,
                self.tax_amount,
            )
        ):
            raise ValueError("Tax values must be finite.")

        if self.taxable_base < Decimal("0"):
            raise ValueError("Taxable base cannot be negative.")

        if self.tax_rate < Decimal("0"):
            raise ValueError("Tax rate cannot be negative.")

        if self.tax_rate > Decimal("100"):
            raise ValueError("Tax rate cannot exceed 100%.")

        if self.tax_amount < Decimal("0"):
            raise ValueError("Tax amount cannot be negative.")

        expected_amount = (
            self.taxable_base * self.tax_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if self.tax_amount != expected_amount:
            raise ValueError(
                "Tax amount does not match taxable base and rate."
            )
