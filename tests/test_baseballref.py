from fakes import FakeWeb
from fixtures import testdatadir
from mlbstandings.baseballref import BaseballReference

from datetime import date


def test_first_day(testdatadir: str) -> None:
    web = FakeWeb(testdatadir)
    bref = BaseballReference(web)
    assert bref.first_day(date(2023, 1, 1)) == date(2023, 3, 30)
