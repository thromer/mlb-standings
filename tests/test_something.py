from fakes import *
from mlbstandings.updater import Updater

from zoneinfo import ZoneInfo
from datetime import datetime


def test_something() -> None:
    now = datetime(2023, 3, 31, tzinfo=ZoneInfo("America/Los_Angeles"))
    drive = FakeDrive()  # TODO: Actually set it up
    sheets = FakeSpreadsheets()  # TODO set it up
    web = FakeWeb('test-data')  # TODO: is relative path ok here ???
    u = Updater(now, drive, sheets, web)
    u.update()
    # TODO: see what results we got
