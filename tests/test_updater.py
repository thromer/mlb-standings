"""Test updater.py"""
from datetime import datetime
from zoneinfo import ZoneInfo
from fixtures import testdatadir

import fakes
import mlbstandings.google_wrappers
import mlbstandings.updater
import mlbstandings.web


def test_empty_unknown_opening_day() -> None:
    """Opening day unknown, don't do anything"""
    pass


def test_empty_before_opening_day() -> None:
    """Opening day known, so fill in openingDay-1 row"""
    pass


# def test_empty_opening_day_done() -> None:
#     """Have data from first day"""
#     pass


def test_zero_row_opening_day_done() -> None:
    """Add data from first day"""
    pass


def test_zero_row_multiple_days_done(testdatadir: str) -> None:
    """Add data from multiple days"""
    now = datetime(2023, 3, 30, tzinfo=ZoneInfo('America/Los_Angeles'))
    drive = fakes.FakeDrive()
    spreadsheets = fakes.FakeSpreadsheets()
    web = fakes.FakeWeb(testdatadir)
    updater = mlbstandings.updater.Updater(now, drive, spreadsheets, web)
    # TODO updater.update()
    # TOOD get the data from the spreadsheet and compare to expected
    # assert False
