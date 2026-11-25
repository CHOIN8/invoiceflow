
from decimal import Decimal, ROUND_HALF_UP

from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.models.withholding import Withholding
from invoiceflow.models.payment import Payment

from invoiceflow.models.adjustment import (
    Adjustment,
    AdjustmentTaxTreatment,
    AdjustmentType,
)


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
    def calculate_adjusted_taxable_base(
        tax_breakdowns: list[TaxBreakdown],
        adjustments: list[Adjustment] | None = None,
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

        if adjustments is None:
            adjustments = []

        if not isinstance(adjustments, list):
            raise TypeError("Adjustments must be a list.")

        if not all(
            isinstance(item, Adjustment)
            for item in adjustments
        ):
            raise TypeError(
                "All adjustment items must be Adjustment instances."
            )

        available_bases = {}

        for item in tax_breakdowns:
            available_bases[item.tax_rate] = (
                available_bases.get(item.tax_rate, Decimal("0"))
                + item.taxable_base
            )

        adjusted_base = sum(
            (item.taxable_base for item in tax_breakdowns),
            Decimal("0"),
        )

        for adjustment in adjustments:
            if (
                adjustment.tax_treatment
                != AdjustmentTaxTreatment.BEFORE_TAX
            ):
                continue

            if adjustment.adjustment_type == AdjustmentType.DISCOUNT:
                available_base = available_bases.get(
                    adjustment.tax_rate,
                    Decimal("0"),
                )

                if adjustment.amount > available_base:
                    raise ValueError(
                        "Discount exceeds taxable base for its tax rate."
                    )

                available_bases[adjustment.tax_rate] -= adjustment.amount
                adjusted_base -= adjustment.amount

            else:
                adjusted_base += adjustment.amount

        return InvoiceCalculator.round_amount(adjusted_base)

    @staticmethod
    def calculate_total(
        tax_breakdowns: list[TaxBreakdown],
        withholdings: list[Withholding],
        adjustments: list[Adjustment] | None = None,
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

        if adjustments is None:
            adjustments = []

        if not isinstance(adjustments, list):
            raise TypeError("Adjustments must be a list.")

        if not all(
            isinstance(item, Adjustment)
            for item in adjustments
        ):
            raise TypeError(
                "All adjustment items must be Adjustment instances."
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

        available_bases = {}

        for item in tax_breakdowns:
            available_bases[item.tax_rate] = (
                available_bases.get(item.tax_rate, Decimal("0"))
                + item.taxable_base
            )

        for adjustment in adjustments:
            sign = (
                Decimal("-1")
                if adjustment.adjustment_type == AdjustmentType.DISCOUNT
                else Decimal("1")
            )

            if adjustment.tax_treatment == AdjustmentTaxTreatment.BEFORE_TAX:
                tax_rate = adjustment.tax_rate

                if adjustment.adjustment_type == AdjustmentType.DISCOUNT:
                    available_base = available_bases.get(
                        tax_rate,
                        Decimal("0"),
                    )

                    if adjustment.amount > available_base:
                        raise ValueError(
                            "Discount exceeds taxable base for its tax rate."
                        )

                    available_bases[tax_rate] -= adjustment.amount

                adjustment_tax = InvoiceCalculator.calculate_tax(
                    adjustment.amount,
                    tax_rate,
                )

                total += sign * (adjustment.amount + adjustment_tax)

            else:
                total += sign * adjustment.amount

        return InvoiceCalculator.round_amount(total)
    @staticmethod
    def calculate_paid_amount(payments: list[Payment]) -> Decimal:
        if not isinstance(payments, list):
            raise TypeError("Payments must be a list.")

        if not all(isinstance(item, Payment) for item in payments):
            raise TypeError(
                "All payment items must be Payment instances."
            )

        total_paid = sum(
            (payment.amount for payment in payments),
            Decimal("0"),
        )

        return InvoiceCalculator.round_amount(total_paid)

    @staticmethod
    def calculate_balance(
        invoice_total: Decimal,
        payments: list[Payment],
    ) -> Decimal:
        if not isinstance(invoice_total, Decimal):
            raise TypeError("Invoice total must be a Decimal.")

        if not invoice_total.is_finite():
            raise ValueError("Invoice total must be finite.")

        if invoice_total < Decimal("0"):
            raise ValueError("Invoice total cannot be negative.")

        paid_amount = InvoiceCalculator.calculate_paid_amount(payments)

        return InvoiceCalculator.round_amount(
            invoice_total - paid_amount
        )
