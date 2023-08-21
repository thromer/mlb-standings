from fakes import FakeWeb
from mlbstandings.baseballref import BaseballReference

from datetime import datetime


def test_first_day(testdatadir: str) -> None:
    web = FakeWeb(testdatadir)
    bref = BaseballReference(web)
    assert bref.first_day(datetime(2023, 1, 1)) == datetime(2023, 3, 30)
