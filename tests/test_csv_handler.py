
from datetime import date
from decimal import Decimal

import pytest

from invoiceflow.export.csv_handler import (
    export_invoices_csv,
    import_invoices_csv,
)
from invoiceflow.models.invoice import Invoice
from invoiceflow.models.tax_breakdown import TaxBreakdown
from invoiceflow.models.withholding import Withholding
from invoiceflow.models.adjustment import (
    Adjustment,
    AdjustmentType,
    AdjustmentTaxTreatment,
)
from invoiceflow.models.payment import Payment


def create_invoice():
    return Invoice(
        invoice_number="INV-001",
        issue_date=date(2026, 11, 24),
        supplier_name="Proveedor de prueba",
        supplier_tax_id="B12345678",
        tax_breakdown=[
            TaxBreakdown(
                taxable_base=Decimal("1000.00"),
                tax_rate=Decimal("21"),
                tax_amount=Decimal("210.00"),
            )
        ],
        withholdings=[
            Withholding(
                concept="Retención IRPF",
                taxable_base=Decimal("1000.00"),
                rate=Decimal("15"),
                amount=Decimal("150.00"),
            )
        ],
        adjustments=[
            Adjustment(
                concept="Descuento comercial",
                adjustment_type=AdjustmentType.DISCOUNT,
                tax_treatment=AdjustmentTaxTreatment.BEFORE_TAX,
                amount=Decimal("50.00"),
                tax_rate=Decimal("21"),
            ),
            Adjustment(
                concept="Gastos adicionales",
                adjustment_type=AdjustmentType.SURCHARGE,
                tax_treatment=AdjustmentTaxTreatment.AFTER_TAX,
                amount=Decimal("20.00"),
            ),
        ],
        payments=[
            Payment(
                payment_date=date(2026, 11, 25),
                amount=Decimal("500.00"),
                method="Transferencia",
                reference="TRF-001",
            )
        ],
        due_date=date(2026, 12, 24),
        currency="EUR",
        document_total=Decimal("1000.00"),
    )


def test_csv_export_and_import_preserve_invoice(tmp_path):
    invoice = create_invoice()
    file_path = tmp_path / "invoices.csv"

    export_invoices_csv([invoice], file_path)
    imported = import_invoices_csv(file_path)

    assert len(imported) == 1
    assert imported[0] == invoice


def test_csv_export_and_import_preserve_empty_invoice_lists(tmp_path):
    invoice = Invoice(
        invoice_number="INV-002",
        issue_date=date(2026, 11, 24),
        supplier_name="Proveedor sin detalles",
        supplier_tax_id="B87654321",
    )
    file_path = tmp_path / "empty_invoice.csv"

    export_invoices_csv([invoice], file_path)
    imported = import_invoices_csv(file_path)

    assert imported == [invoice]


def test_csv_export_and_import_preserve_multiple_invoices(tmp_path):
    invoices = [
        create_invoice(),
        Invoice(
            invoice_number="INV-003",
            issue_date=date(2026, 11, 24),
            supplier_name="Segundo proveedor",
            supplier_tax_id="B11223344",
        ),
    ]
    file_path = tmp_path / "multiple_invoices.csv"

    export_invoices_csv(invoices, file_path)
    imported = import_invoices_csv(file_path)

    assert imported == invoices


def test_csv_import_rejects_invalid_headers(tmp_path):
    file_path = tmp_path / "invalid.csv"
    file_path.write_text("wrong_header\nvalue\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid InvoiceFlow format"):
        import_invoices_csv(file_path)


def test_csv_import_reports_invalid_invoice_row(tmp_path):
    file_path = tmp_path / "invalid_invoice.csv"
    file_path.write_text(
        "id,invoice_number,issue_date,supplier_name,supplier_tax_id,"
        "tax_breakdown,withholdings,adjustments,payments,due_date,"
        "currency,document_total,invoice_type,original_invoice_number,"
        "original_invoice_id,rectification_reason\n"
        "invalid,INV-001,2026-11-24,Proveedor,B12345678,"
        "[],[],[],[],,EUR,,standard,,,\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="CSV row 2"):
        import_invoices_csv(file_path)


def test_csv_export_rejects_non_invoice_items(tmp_path):
    with pytest.raises(TypeError, match="Invoice instances"):
        export_invoices_csv(["not an invoice"], tmp_path / "invalid.csv")


def test_csv_export_rejects_non_list_input(tmp_path):
    with pytest.raises(TypeError, match="list"):
        export_invoices_csv("not a list", tmp_path / "invalid.csv")
