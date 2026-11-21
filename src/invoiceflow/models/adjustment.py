
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

    def __post_init__(self):
        if not isinstance(self.concept, str):
            raise TypeError("Adjustment concept must be a string.")

        if not self.concept.strip():
            raise ValueError("Adjustment concept cannot be empty.")

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
