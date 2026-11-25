# InvoiceFlow

InvoiceFlow is a Python-based invoice processing engine designed to automate the extraction, validation, calculation, import and export of received supplier invoices.

## Initial Scope

The first version focuses exclusively on received supplier invoices.

The project is designed as an independent Python engine, with the possibility of adding a desktop interface in the future.

## Current Features

### Invoice Management
- Invoice data models and validation.
- Support for standard and rectifying invoices.
- Multiple VAT breakdowns.
- Withholding tax support.
- Discounts and surcharges.
- Payment records.
- Invoice identification using UUIDs.

### Financial Calculations
- Financial calculations using Python's `Decimal`.
- Monetary rounding using `ROUND_HALF_UP`.
- Invoice total calculations.
- Payment tracking and outstanding balance calculations.
- Validation of document totals against calculated totals.

### Document Processing
- Text extraction from digital PDF invoices.
- OCR support for scanned PDF documents.
- OCR support for image files.
- Spanish and English OCR language support.
- Automatic extraction of key invoice information.
- Confidence assessment for extracted fields.
- Manual review flags for uncertain or inconsistent data.

### Data Import and Export
- CSV invoice export.
- CSV invoice import.
- Preservation of invoice data, including nested tax breakdowns, withholdings, adjustments and payments.
- Excel (`.xlsx`) invoice export.
- Excel formatting with headers, filters and automatic column sizing.

## Technology

- Python 3.12+
- PyMuPDF for PDF processing.
- Tesseract OCR through Pytesseract.
- OpenPyXL for Excel export.
- Pytest for automated testing.
- Decimal for accurate financial calculations.

## OCR Configuration

InvoiceFlow uses Tesseract OCR to process scanned documents and images.

Tesseract must be installed separately. If it is not available through the system PATH, configure its executable location using the `TESSERACT_CMD` environment variable.

Spanish and English language data must also be installed in Tesseract.

## Testing

The project includes an automated test suite using Pytest.

Run the complete test suite with:

```bash
pytest
```

Current test status: 281 tests passing.

## Project Status

Version 0.1.0 - Initial functional version under development.

The core invoice processing engine, document extraction, validation, CSV import/export and Excel export are implemented.