
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from invoiceflow.export.csv_handler import CSV_FIELDS, _invoice_to_row
from invoiceflow.models.invoice import Invoice


def export_invoices_excel(
    invoices: list[Invoice],
    file_path: str | Path,
) -> None:
    """Export invoices to an Excel workbook."""

    if not isinstance(invoices, list):
        raise TypeError("Invoices must be provided as a list.")

    if not all(isinstance(invoice, Invoice) for invoice in invoices):
        raise TypeError("All items must be Invoice instances.")

    file_path = Path(file_path)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Invoices"

    worksheet.append(CSV_FIELDS)

    for invoice in invoices:
        row = _invoice_to_row(invoice)
        worksheet.append([row[field] for field in CSV_FIELDS])

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78",
    )

    for cell in worksheet[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF",
        )
        cell.fill = header_fill

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column in worksheet.columns:
        column_letter = get_column_letter(column[0].column)
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )
        worksheet.column_dimensions[column_letter].width = min(
            max_length + 2,
            50,
        )

    workbook.save(file_path)
