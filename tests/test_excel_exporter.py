
from datetime import date
from decimal import Decimal

import pytest
from openpyxl import load_workbook

from invoiceflow.export.excel_exporter import export_invoices_excel
from invoiceflow.models.invoice import Invoice


def create_invoice():
    return Invoice(
        invoice_number="INV-EXCEL-001",
        issue_date=date(2026, 11, 25),
        supplier_name="Proveedor Excel",
        supplier_tax_id="B12345678",
        currency="EUR",
        document_total=Decimal("1210.00"),
    )


def test_excel_export_creates_workbook(tmp_path):
    invoice = create_invoice()
    file_path = tmp_path / "invoices.xlsx"

    export_invoices_excel([invoice], file_path)

    assert file_path.exists()

    workbook = load_workbook(file_path)
    assert "Invoices" in workbook.sheetnames


def test_excel_export_preserves_invoice_data(tmp_path):
    invoice = create_invoice()
    file_path = tmp_path / "invoices.xlsx"

    export_invoices_excel([invoice], file_path)

    workbook = load_workbook(file_path)
    worksheet = workbook["Invoices"]

    headers = [
        cell.value
        for cell in worksheet[1]
    ]

    row = dict(
        zip(
            headers,
            [cell.value for cell in worksheet[2]],
        )
    )

    assert row["invoice_number"] == invoice.invoice_number
    assert row["supplier_name"] == invoice.supplier_name
    assert row["supplier_tax_id"] == invoice.supplier_tax_id
    assert row["document_total"] == "1210.00"
    assert row["issue_date"] == "2026-11-25"
    assert row["id"] == str(invoice.id)


def test_excel_export_applies_worksheet_formatting(tmp_path):
    invoice = create_invoice()
    file_path = tmp_path / "invoices.xlsx"

    export_invoices_excel([invoice], file_path)

    workbook = load_workbook(file_path)
    worksheet = workbook["Invoices"]

    assert worksheet.freeze_panes == "A2"
    assert worksheet.auto_filter.ref == worksheet.dimensions
    assert worksheet["A1"].font.bold is True
    assert worksheet["A1"].fill.fill_type == "solid"


def test_excel_export_supports_empty_invoice_list(tmp_path):
    file_path = tmp_path / "empty.xlsx"

    export_invoices_excel([], file_path)

    workbook = load_workbook(file_path)
    worksheet = workbook["Invoices"]

    assert worksheet.max_row == 1


def test_excel_export_rejects_non_list_input(tmp_path):
    with pytest.raises(TypeError, match="list"):
        export_invoices_excel(
            "not a list",
            tmp_path / "invalid.xlsx",
        )


def test_excel_export_rejects_non_invoice_items(tmp_path):
    with pytest.raises(TypeError, match="Invoice instances"):
        export_invoices_excel(
            ["not an invoice"],
            tmp_path / "invalid.xlsx",
        )
