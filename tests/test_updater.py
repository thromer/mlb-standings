"""Test updater.py"""
import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from fixtures import TEST_DATA_DIR

import fakes
import mlbstandings.google_wrappers
import mlbstandings.updater
import mlbstandings.web
from mlbstandings.helpers import date_from_excel_date


def test_empty_unknown_opening_day() -> None:
    """Opening day unknown, don't do anything"""
    pass


@pytest.mark.datafiles(TEST_DATA_DIR / 'test_empty_before_opening_day_sheet')
def test_empty_before_opening_day(datafiles: pathlib.Path) -> None:
    """Opening day known (from schedule) so fill in openingDay-1 row"""
    for f in datafiles.iterdir():
        print(f.name)
    now = datetime(2023, 3, 30, tzinfo=ZoneInfo('America/Los_Angeles'))
    drive = fakes.FakeDrive({'MLB Standings 2023': datafiles})
    spreadsheets = fakes.FakeSpreadsheets(datafiles)
    web = fakes.FakeWeb(TEST_DATA_DIR)
    try:
        updater = mlbstandings.updater.Updater(now, drive, spreadsheets, web)
        updater.update()
    finally:
        spreadsheets.close()
    spreadsheet = spreadsheets.spreadsheet(drive.get_spreadsheet_id('MLB Standings 2023'))
    first_day_val = spreadsheet.get_named_cell('first_day')
    if type(first_day_val) is not int:
        raise TypeError(f'{first_day_val} has type {type(first_day_val)}')
    print(f"first_day={date_from_excel_date(first_day_val)}")


# def test_empty_opening_day_done() -> None:
#     """Have data from first day"""
#     pass


def test_zero_row_opening_day_done() -> None:
    """Add data from first day"""
    pass


@pytest.mark.datafiles(TEST_DATA_DIR / 'test_zero_row_multiple_days_done_sheet')
def test_zero_row_multiple_days_done(datafiles: pathlib.Path) -> None:
    """Add data from multiple days"""
    now = datetime(2023, 5, 1, tzinfo=ZoneInfo('America/Los_Angeles'))
    drive = fakes.FakeDrive({'MLB Standings 2023': datafiles})
    spreadsheets = fakes.FakeSpreadsheets(datafiles)
    web = fakes.FakeWeb(TEST_DATA_DIR)
    try:
        updater = mlbstandings.updater.Updater(now, drive, spreadsheets, web)
        updater.update()
    finally:
        spreadsheets.close()
    # TOOD get the data from the spreadsheet (or somewhere) and compare to expected
    # assert False
