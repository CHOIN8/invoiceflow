
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class AdjustmentType(Enum):
    DISCOUNT = "discount"
    SURCHARGE = "surcharge"


class AdjustmentTaxTreatment(Enum):
    BEFORE_TAX = "before_tax"
    AFTER_TAX = "after_tax"


@dataclass
class Adjustment:
    concept: str
    adjustment_type: AdjustmentType
    tax_treatment: AdjustmentTaxTreatment
    amount: Decimal
    tax_rate: Decimal | None = None

    def __post_init__(self):
        if not isinstance(self.concept, str):
            raise TypeError("Adjustment concept must be a string.")

        if not self.concept.strip():
            raise ValueError("Adjustment concept cannot be empty.")

        self.concept = self.concept.strip()

        if not isinstance(self.adjustment_type, AdjustmentType):
            raise TypeError("Invalid adjustment type.")

        if not isinstance(self.tax_treatment, AdjustmentTaxTreatment):
            raise TypeError("Invalid tax treatment.")

        if not isinstance(self.amount, Decimal):
            raise TypeError("Adjustment amount must be a Decimal.")

        if not self.amount.is_finite():
            raise ValueError("Adjustment amount must be finite.")

        if self.amount < Decimal("0"):
            raise ValueError("Adjustment amount cannot be negative.")

        if self.tax_treatment == AdjustmentTaxTreatment.BEFORE_TAX:
            if self.tax_rate is None:
                raise ValueError(
                    "Before-tax adjustments must include a tax rate."
                )

        elif self.tax_rate is not None:
            raise ValueError(
                "After-tax adjustments cannot include a tax rate."
            )

        if self.tax_rate is not None:
            if not isinstance(self.tax_rate, Decimal):
                raise TypeError("Adjustment tax rate must be a Decimal.")

            if not self.tax_rate.is_finite():
                raise ValueError("Adjustment tax rate must be finite.")

            if self.tax_rate < Decimal("0") or self.tax_rate > Decimal("100"):
                raise ValueError(
                    "Adjustment tax rate must be between 0 and 100."
                )
