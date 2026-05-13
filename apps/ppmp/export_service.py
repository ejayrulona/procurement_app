"""
Annual Procurement Plan (APP) - Excel Export Service

Calibrated to the official WMSU APP Template.

Column mapping (APP section only, cols A–N):
  A  = Code (PAP) → formula =C{row}  (auto-derived)
  B  = Procurement Program/Project
  C  = Object Code
  D  = PMO/End-User
  E  = Mode of Procurement
  F  = Advertisement/Posting of IB/REI  
  G  = Submission/Opening of Bids
  H  = Notice of Award                  
  I  = Contract Signing                 
  J  = Source of Funds
  K  = Total (Estimated Budget) → formula =L{row}+M{row}
  L  = MOOE
  M  = CO
  N  = Remarks
"""

import io
from datetime import date, datetime
from typing import Optional
from openpyxl import load_workbook
from openpyxl.styles import Alignment

# CONSTANTS — matched to the real template

DATA_START_ROW = 5   # First data row in the template (rows 1-4 are headers)

CURRENCY_FMT = '#,##0.00'
DATE_FMT = 'MMM-YY'   # (e.g. Jan-26)


# PUBLIC API

def generate_app_excel(
    records: list[dict],
    template_path: str,
) -> bytes:
    """
    Populate the official APP Excel template with procurement records.

    Steps:
      1. Load the template (preserves all formatting, merged cells, headers)
      2. Clear existing data rows (values only — formatting stays intact)
      3. Write new records starting at DATA_START_ROW
      4. Serialize to bytes and return

    Parameters
    
    records : list[dict]
        Each dict should contain:

        {
            "program_project":     str,
            "object_code":         str,
            "pmo_end_user":        str,
            "mode_of_procurement": str,
            "advert_date":         date | datetime | str | None,
            "submission_date":     date | datetime | str | None,
            "notice_date":         date | datetime | str | None,
            "contract_signing":    date | datetime | str | None,
            "source_of_funds":     str,
            "mooe":                float | int | None,
            "co":                  float | int | None,
            "remarks":             str | None,
        }

        Note: "code_pap" (col A) and "total" (col K) are auto-computed
        via Excel formulas you do NOT need to supply them.

    template_path : str
        Absolute path to the official .xlsx template file.

    Returns
    
    bytes
        Raw .xlsx bytes ready to stream as an HTTP file-download response.
    """
    wb = load_workbook(template_path)
    ws = wb.active

    _clear_data_rows(ws, DATA_START_ROW, ws.max_row)

    for i, record in enumerate(records):
        _write_record_row(ws, DATA_START_ROW + i, record)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


# CLEAR  — wipe values only, preserve all cell formatting

def _clear_data_rows(ws, start_row: int, end_row: int):
    """
    Set cell values to None for every cell in the data area.
    Formatting (borders, fills, fonts, number formats) is left untouched
    so the template's visual style survives between exports.
    """

    for row in ws.iter_rows(min_row=start_row, max_row=end_row):
        for cell in row:
            cell.value = None


# WRITE  — one record → one row

def _write_record_row(ws, row: int, rec: dict):
    # Write one procurement record into the given Excel row.

    # A: Code (PAP) — formula mirrors Object Code (col C), same as template
    ws[f"A{row}"] = f"=C{row}"

    # B: Procurement Program/Project
    _set(ws, f"B{row}", rec.get("program_project"), wrap=True)

    # C: Object Code — stored as text to preserve leading zeros
    cell_c = ws[f"C{row}"]
    cell_c.value = str(rec.get("object_code") or "")
    cell_c.number_format = "@"

    # D: PMO/End-User
    _set(ws, f"D{row}", rec.get("pmo_end_user"))

    # E: Mode of Procurement
    _set(ws, f"E{row}", rec.get("mode_of_procurement"), wrap=True)

    # F–I: Schedule dates
    _set_date(ws, f"F{row}", rec.get("advertisement_date"))
    _set_date(ws, f"G{row}", rec.get("submission_date"))
    _set_date(ws, f"H{row}", rec.get("notice_of_award_date"))
    _set_date(ws, f"I{row}", rec.get("contract_signing_date"))

    # J: Source of Funds
    _set(ws, f"J{row}", rec.get("source_of_funds"), wrap=True)

    # K: Total — formula (MOOE + CO), same pattern as template
    ws[f"K{row}"] = f"=L{row}+M{row}"
    ws[f"K{row}"].number_format = CURRENCY_FMT

    # L: MOOE
    _set_currency(ws, f"L{row}", rec.get("mooe"))

    # M: CO
    _set_currency(ws, f"M{row}", rec.get("co"))

    # N: Remarks
    _set(ws, f"N{row}", rec.get("remarks"), wrap=True)


# CELL HELPERS

def _set(ws, addr: str, value, wrap: bool = False):
    # Write a plain string value; treats None/dash as blank.

    cell = ws[addr]
    cell.value = None if value in (None, "", "—", "–", "--") else str(value)
    if wrap:
        existing = cell.alignment
        cell.alignment = Alignment(
            wrap_text=True,
            vertical=getattr(existing, "vertical", None) or "top",
            horizontal=getattr(existing, "horizontal", None) or "left",
        )


def _set_date(ws, addr: str, value):
    """
    Write a date/datetime.  Accepts datetime, date, ISO string, or None.
    Applies MMM-YY number format to match the template's display style.
    """

    cell = ws[addr]
    if value in (None, "", "—", "–", "--"):
        cell.value = None
        return
    if isinstance(value, datetime):
        cell.value = value
    elif isinstance(value, date):
        cell.value = datetime(value.year, value.month, value.day)
    elif isinstance(value, str):
        try:
            cell.value = datetime.fromisoformat(value)
        except ValueError:
            cell.value = value  # store as-is if unparseable
    else:
        cell.value = value
    cell.number_format = DATE_FMT


def _set_currency(ws, addr: str, value):
    # Write a numeric value with currency formatting; None stays blank.

    cell = ws[addr]
    if value in (None, ""):
        cell.value = None
        return
    try:
        cell.value = float(value)
    except (ValueError, TypeError):
        cell.value = None
    cell.number_format = CURRENCY_FMT