"""Test updater.py"""
import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import mlbstandings.updater
from mlbstandings.helpers import date_from_excel_date

from .fakes import FakeFiles, FakeSpreadsheets, FakeWeb
from .fixtures import TEST_DATA_DIR

CONTENTS_SHEET_ID = 'contents'


def test_empty_unknown_opening_day() -> None:
    """Opening day unknown, don't do anything"""
    pass


@pytest.mark.datafiles(TEST_DATA_DIR / 'test_empty_before_opening_day_spreadsheets')
def test_empty_before_opening_day(datafiles: pathlib.Path) -> None:
    """Opening day known (from schedule) so fill in openingDay-1 row"""
    for f in datafiles.iterdir():
        print(f.name)
    now = datetime(2023, 3, 30, tzinfo=ZoneInfo('America/Los_Angeles'))
    spreadsheets = FakeSpreadsheets(datafiles)
    files = FakeFiles()
    web = FakeWeb(TEST_DATA_DIR)
    try:
        updater = mlbstandings.updater.Updater(now, files, spreadsheets, CONTENTS_SHEET_ID, web)
        updater.update()
    finally:
        spreadsheets.close()
    spreadsheet = spreadsheets.spreadsheet(updater.get_spreadsheet_id_for_year(2023))
    first_day_val = spreadsheet.get_cell('first_day')
    if type(first_day_val) is not int:
        raise TypeError(f'{first_day_val} has type {type(first_day_val)}')
    print(f"first_day={date_from_excel_date(first_day_val)}")


# def test_empty_opening_day_done() -> None:
#     """Have data from first day"""
#     pass


def test_zero_row_opening_day_done() -> None:
    """Add data from first day"""
    pass


@pytest.mark.datafiles(TEST_DATA_DIR / 'test_zero_row_multiple_days_done_spreadsheets')
def test_zero_row_multiple_days_done(datafiles: pathlib.Path) -> None:
    """Add data from multiple days"""
    now = datetime(2023, 5, 1, tzinfo=ZoneInfo('America/Los_Angeles'))
    spreadsheets = FakeSpreadsheets(datafiles)
    files = FakeFiles()
    web = FakeWeb(TEST_DATA_DIR)
    try:
        updater = mlbstandings.updater.Updater(now, files, spreadsheets, CONTENTS_SHEET_ID, web)
        updater.update()
    finally:
        spreadsheets.close()
    # TOOD get the data from the spreadsheet (or somewhere) and compare to expected
    # assert False
