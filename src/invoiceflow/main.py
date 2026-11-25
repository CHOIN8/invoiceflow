
import argparse

from invoiceflow.document import Document
from invoiceflow.document_processor import DocumentProcessor
from invoiceflow.extraction.invoice_extractor import InvoiceExtractor
from invoiceflow.validation.field_validator import validate_extracted_data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InvoiceFlow - Supplier Invoice Processing Engine"
    )

    parser.add_argument(
        "file",
        help="Path to the invoice PDF or image.",
    )

    args = parser.parse_args()

    try:
        document = Document(args.file)
        processor = DocumentProcessor()
        extracted_text = processor.process(document)

        if not extracted_text:
            print("No text could be extracted from the document.")
            return 1

        extractor = InvoiceExtractor()
        invoice_data = extractor.extract(extracted_text)

        validation = validate_extracted_data(invoice_data)

    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    print("\nInvoiceFlow - Extracted Invoice Data")
    print("=" * 50)

    print(f"Invoice number: {invoice_data.invoice_number}")
    print(f"Issue date: {invoice_data.issue_date}")
    print(f"Supplier: {invoice_data.supplier_name}")
    print(f"Supplier tax ID: {invoice_data.supplier_tax_id}")
    print(f"Taxable base: {invoice_data.taxable_base}")

    print("VAT breakdown:")
    if invoice_data.tax_breakdowns:
        for breakdown in invoice_data.tax_breakdowns:
            print(
                f"- Base: {breakdown.taxable_base} | "
                f"Rate: {breakdown.tax_rate}% | "
                f"VAT: {breakdown.tax_amount}"
            )
    else:
        print("- No tax breakdown available.")

    print(f"VAT amount: {invoice_data.vat_amount}")
    print(f"Total amount: {invoice_data.total_amount}")
    print("=" * 50)

    if validation.errors:
        print("Errors:")
        for error in validation.errors:
            print(f"- {error}")
    else:
        print("Errors: None")

    if validation.warnings:
        print("Warnings:")
        for warning in validation.warnings:
            print(f"- {warning}")
    else:
        print("Warnings: None")

    print(f"\nRequires review: {validation.requires_review}")

    return 1 if validation.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
