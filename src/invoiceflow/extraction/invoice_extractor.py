
import re
from datetime import datetime
from decimal import Decimal

from invoiceflow.confidence import ConfidenceLevel
from invoiceflow.extracted_data import ExtractedInvoiceData
from invoiceflow.models.tax_breakdown import TaxBreakdown


class InvoiceExtractor:
    """Extracts basic invoice fields from document text."""

    AMOUNT_PATTERN = r"\d{1,3}(?:\.\d{3})*,\d{2}"

    def extract(self, text: str) -> ExtractedInvoiceData:
        if not isinstance(text, str):
            raise TypeError("Text must be a string.")

        if not text.strip():
            raise ValueError("Text cannot be empty.")

        invoice_number = None
        issue_date = None
        supplier_name = None
        supplier_tax_id = None
        taxable_base = None
        vat_amount = None
        total_amount = None
        tax_breakdowns = []

        confidence = {}

        # Supplier name and tax ID.
        client_section_match = re.search(
            r"^\s*CLIENTE\s*$",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        supplier_section = (
            text[:client_section_match.start()]
            if client_section_match
            else text
        )

        tax_id_match = re.search(
            r"^\s*NIF/CIF\s*:\s*([A-Z0-9-]+)\s*$",
            supplier_section,
            re.IGNORECASE | re.MULTILINE,
        )

        if tax_id_match:
            supplier_tax_id = tax_id_match.group(1).upper()
            confidence["supplier_tax_id"] = ConfidenceLevel.HIGH

            preceding_lines = [
                line.strip()
                for line in supplier_section[:tax_id_match.start()].splitlines()
                if line.strip()
            ]

            if preceding_lines:
                supplier_name = preceding_lines[0]
                confidence["supplier_name"] = ConfidenceLevel.MEDIUM

        # Invoice date and number.
        header_match = re.search(
            r"(\d{2}[-/]\d{2}[-/]\d{4})\s+(\d+)\s+1",
            text,
        )

        if header_match:
            issue_date = datetime.strptime(
                header_match.group(1).replace("/", "-"),
                "%d-%m-%Y",
            ).date()

            invoice_number = header_match.group(2)

            confidence["issue_date"] = ConfidenceLevel.HIGH
            confidence["invoice_number"] = ConfidenceLevel.HIGH

        # Extract tax breakdowns.
        tax_pattern = re.compile(
            rf"({self.AMOUNT_PATTERN})\s+"
            rf"(21|10|4)(?:[,.]0+)?\s+"
            rf"({self.AMOUNT_PATTERN})"
        )

        tax_section_match = re.search(
            r"Base imponible([\s\S]{0,500}?)"
            r"(?:Forma de pago|TOTAL FACTURA)",
            text,
            re.IGNORECASE,
        )

        if tax_section_match:
            tax_section = tax_section_match.group(1)

            for match in tax_pattern.finditer(tax_section):
                base = self._parse_amount(match.group(1))
                rate = Decimal(match.group(2))
                amount = self._parse_amount(match.group(3))

                tax_breakdowns.append(
                    TaxBreakdown(
                        taxable_base=base,
                        tax_rate=rate,
                        tax_amount=amount,
                    )
                )

        # Aggregate taxable base and VAT amount.
        if tax_breakdowns:
            taxable_base = sum(
                (item.taxable_base for item in tax_breakdowns),
                Decimal("0"),
            )

            vat_amount = sum(
                (item.tax_amount for item in tax_breakdowns),
                Decimal("0"),
            )

            confidence["taxable_base"] = ConfidenceLevel.HIGH
            confidence["vat_amount"] = ConfidenceLevel.HIGH

        # Invoice total.
        total_match = re.search(
            r"TOTAL FACTURA\s+"
            r"[\d.]+,\d{2}\s+"
            r"[\d.]+[,.]\d{2}\s+"
            rf"({self.AMOUNT_PATTERN})",
            text,
            re.IGNORECASE,
        )

        if total_match:
            total_amount = self._parse_amount(total_match.group(1))
            confidence["total_amount"] = ConfidenceLevel.HIGH
            if (
                taxable_base is not None
                and vat_amount is not None
                and total_amount is not None
                and total_amount != taxable_base + vat_amount
            ):
                confidence["total_amount"] = ConfidenceLevel.MEDIUM
        return ExtractedInvoiceData(
            invoice_number=invoice_number,
            issue_date=issue_date,
            supplier_name=supplier_name,
            supplier_tax_id=supplier_tax_id,
            taxable_base=taxable_base,
            vat_amount=vat_amount,
            total_amount=total_amount,
            tax_breakdowns=tax_breakdowns,
            confidence=confidence,
        )

    @staticmethod
    def _parse_amount(value: str) -> Decimal:
        normalized = value.replace(".", "").replace(",", ".")
        return Decimal(normalized)
