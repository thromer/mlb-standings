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


def test_empty_unknown_opening_day() -> None:
    """Opening day unknown, don't do anything"""
    pass


@pytest.mark.datafiles(TEST_DATA_DIR / 'fun.csv', TEST_DATA_DIR / 'fun.json')
def example_test_empty_before_opening_day(datafiles: pathlib.PosixPath) -> None:
    """Opening day known, so fill in openingDay-1 row"""
    # for f in datafiles.iterdir():
    #     print(f)
    #     print(f.name)
    pass


# def test_empty_opening_day_done() -> None:
#     """Have data from first day"""
#     pass


def test_zero_row_opening_day_done() -> None:
    """Add data from first day"""
    pass


def test_zero_row_multiple_days_done() -> None:
    """Add data from multiple days"""
    now = datetime(2023, 3, 30, tzinfo=ZoneInfo('America/Los_Angeles'))
    drive = fakes.FakeDrive()
    spreadsheets = fakes.FakeSpreadsheets()
    web = fakes.FakeWeb(TEST_DATA_DIR)
    updater = mlbstandings.updater.Updater(now, drive, spreadsheets, web)
    # TODO updater.update()
    # TOOD get the data from the spreadsheet and compare to expected
    # assert False
