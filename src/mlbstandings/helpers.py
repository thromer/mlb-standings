import datetime
import string
from typing import Tuple

_EXCEL_EPOCH = datetime.date(1900, 1, 1).toordinal() - 2


def date_from_excel_date(sheet_date: int) -> datetime.date:
    return datetime.date.fromordinal(_EXCEL_EPOCH + sheet_date)


def date_to_excel_date(python_date: datetime.date) -> int:
    return datetime.date.fromordinal(python_date.toordinal() - _EXCEL_EPOCH).toordinal()


def sheet_coltoindex(col: str) -> int:
    """Return zero-based index of column given value in A1 format. https://stackoverflow.com/a/45312360"""
    num = 0
    for c in col:
        if c not in string.ascii_letters:
            raise ValueError('Bad column name {col}')
        num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num - 1


def sheet_indextocol(n: int) -> str:
    """Return column name given zero-based column index. https://stackoverflow.com/a/45312360"""
    n = n + 1
    name = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        name = chr(r + ord('A')) + name
    return name


def rc0_to_sheet(rc0: Tuple[int, int]) -> str:
    return sheet_indextocol(rc0[1]) + str(rc0[0])


def rc0_range_to_sheet_range(rc0_range: Tuple[Tuple[int, int], Tuple[int, int]]) -> str:
    """Given start and end rc coordinates (zero-based), return corresponding sheets range string"""
    return rc0_to_sheet(rc0_range[0]) + ':' + rc0_to_sheet(rc0_range[1])
