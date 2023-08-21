import datetime

_EXCEL_EPOCH = datetime.date(1900, 1, 1).toordinal() - 2


def date_from_excel_date(sheet_date: int) -> datetime.date:
    return datetime.date.fromordinal(_EXCEL_EPOCH + sheet_date)


def date_to_excel_date(python_date: datetime.date) -> int:
    return datetime.date.fromordinal(python_date.toordinal() - _EXCEL_EPOCH).toordinal()
