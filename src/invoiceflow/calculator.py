
from decimal import Decimal, ROUND_HALF_UP

from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.models.withholding import Withholding


class InvoiceCalculator:
    """Calculates invoice amounts and validates totals."""

    @staticmethod
    def _validate_base_and_rate(
        taxable_base: Decimal,
        rate: Decimal,
    ) -> None:
        if not isinstance(taxable_base, Decimal):
            raise TypeError("Taxable base must be a Decimal.")

        if not isinstance(rate, Decimal):
            raise TypeError("Rate must be a Decimal.")

        if not taxable_base.is_finite() or not rate.is_finite():
            raise ValueError("Taxable base and rate must be finite.")

        if taxable_base < Decimal("0"):
            raise ValueError("Taxable base cannot be negative.")

        if rate < Decimal("0") or rate > Decimal("100"):
            raise ValueError("Rate must be between 0 and 100.")

    @staticmethod
    def round_amount(amount: Decimal) -> Decimal:
        if not isinstance(amount, Decimal):
            raise TypeError("Amount must be a Decimal.")

        if not amount.is_finite():
            raise ValueError("Amount must be finite.")

        return amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def calculate_tax(
        taxable_base: Decimal,
        tax_rate: Decimal,
    ) -> Decimal:
        InvoiceCalculator._validate_base_and_rate(
            taxable_base,
            tax_rate,
        )

        tax_amount = taxable_base * tax_rate / Decimal("100")

        return InvoiceCalculator.round_amount(tax_amount)

    @staticmethod
    def calculate_withholding(
        taxable_base: Decimal,
        rate: Decimal,
    ) -> Decimal:
        InvoiceCalculator._validate_base_and_rate(
            taxable_base,
            rate,
        )

        withholding_amount = taxable_base * rate / Decimal("100")

        return InvoiceCalculator.round_amount(withholding_amount)

    @staticmethod
    def calculate_total(
        tax_breakdowns: list[TaxBreakdown],
        withholdings: list[Withholding],
    ) -> Decimal:
        if not isinstance(tax_breakdowns, list):
            raise TypeError("Tax breakdowns must be a list.")

        if not all(
            isinstance(item, TaxBreakdown)
            for item in tax_breakdowns
        ):
            raise TypeError(
                "All tax breakdown items must be TaxBreakdown instances."
            )

        if not isinstance(withholdings, list):
            raise TypeError("Withholdings must be a list.")

        if not all(
            isinstance(item, Withholding)
            for item in withholdings
        ):
            raise TypeError(
                "All withholding items must be Withholding instances."
            )

        taxable_bases = sum(
            (item.taxable_base for item in tax_breakdowns),
            Decimal("0"),
        )

        tax_amounts = sum(
            (item.tax_amount for item in tax_breakdowns),
            Decimal("0"),
        )

        withholding_amounts = sum(
            (item.amount for item in withholdings),
            Decimal("0"),
        )

        total = taxable_bases + tax_amounts - withholding_amounts

        return InvoiceCalculator.round_amount(total)
