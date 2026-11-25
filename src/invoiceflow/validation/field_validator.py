
from invoiceflow.extracted_data import ExtractedInvoiceData
from invoiceflow.validation.validation_result import ValidationResult


def validate_extracted_data(
    data: ExtractedInvoiceData,
) -> ValidationResult:
    if not isinstance(data, ExtractedInvoiceData):
        raise TypeError("Data must be an ExtractedInvoiceData instance.")

    result = ValidationResult()

    required_fields = (
        "invoice_number",
        "issue_date",
        "supplier_name",
        "supplier_tax_id",
        "taxable_base",
        "vat_amount",
        "total_amount",
    )

    for field_name in required_fields:
        value = getattr(data, field_name)

        if value is None:
            result.add_error(
                f"Required field '{field_name}' is missing."
            )
            continue

        if data.field_requires_review(field_name):
            result.add_warning(
                f"Field '{field_name}' requires manual review."
            )
    if data.total_matches_components is False:
        result.add_warning(
            "Invoice total does not match taxable base plus VAT. "
            "Manual review is required."
        )
    return result
