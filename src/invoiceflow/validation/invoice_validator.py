
from invoiceflow.calculator import InvoiceCalculator
from invoiceflow.models.invoice import Invoice
from invoiceflow.validation.validation_result import ValidationResult


def validate_invoice(invoice: Invoice) -> ValidationResult:
    if not isinstance(invoice, Invoice):
        raise TypeError("Invoice must be an Invoice instance.")

    result = ValidationResult()

    try:
        calculated_total = InvoiceCalculator.calculate_total(
            tax_breakdowns=invoice.tax_breakdown,
            withholdings=invoice.withholdings,
            adjustments=invoice.adjustments,
        )
    except (TypeError, ValueError) as error:
        result.add_error(str(error))
        calculated_total = None

    if invoice.document_total is None:
        result.add_warning(
            "Document total is missing and cannot be compared."
        )

    elif calculated_total is not None:
        document_total = InvoiceCalculator.round_amount(
            invoice.document_total
        )

        if document_total != calculated_total:
            result.add_warning(
                "Document total does not match calculated total."
            )

    return result
