import re
import string
from datetime import date


_EXCEL_EPOCH = date(1900, 1, 1).toordinal() - 2


def date_from_excel_date(sheet_date: int) -> date:
    return date.fromordinal(_EXCEL_EPOCH + sheet_date)


def date_to_excel_date(python_date: date) -> int:
    return date.fromordinal(python_date.toordinal() - _EXCEL_EPOCH).toordinal()


def sheet_coltoindex(col: str) -> int:
    """Return zero-based index of column given value in A1 format. https://stackoverflow.com/a/45312360"""
    num = 0
    for c in col:
        if c not in string.ascii_letters:
            msg = f"Bad column name {col}"
            raise ValueError(msg)
        num = num * 26 + (ord(c.upper()) - ord("A")) + 1
    return num - 1


def sheet_indextocol(n: int) -> str:
    """Return column name given zero-based column index. https://stackoverflow.com/a/45312360"""
    n = n + 1
    name = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        name = chr(r + ord("A")) + name
    return name


def rc0_to_sheet(rc0: tuple[int, int]) -> str:
    return sheet_indextocol(rc0[1]) + str(rc0[0] + 1)


def rc0_range_to_sheet_range(rc0_range: tuple[tuple[int, int], tuple[int, int]]) -> str:
    """Given start and end rc coordinates (zero-based), return corresponding sheets range string"""
    return rc0_to_sheet(rc0_range[0]) + ":" + rc0_to_sheet(rc0_range[1])


def sheet_to_rc0(sheet_cell: str) -> tuple[int, int]:
    """Produce a rc0 tuple, and set to -1 if row or column is unspecified"""
    m = re.match(r"^([A-Z]+)([1-9]?[0-9]+)$", sheet_cell)
    if m:
        return int(m[2]) - 1, sheet_coltoindex(m[1])
    elif sheet_cell.isnumeric():
        return int(sheet_cell) - 1, -1
    else:
        return -1, sheet_coltoindex(sheet_cell)


def sheet_range_to_rc0_range(
    sheet_range: str,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Given sheets range string, return start and end rc coordinates (zero-based)."""
    elements = sheet_range.split(":", 1)
    if len(elements) == 1:
        elements = elements * 2
    return sheet_to_rc0(elements[0]), sheet_to_rc0(elements[1])
