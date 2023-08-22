from fakes import FakeWeb
from fixtures import TEST_DATA_DIR
from mlbstandings.baseballref import BaseballReference

from datetime import date


def test_first_day() -> None:
    web = FakeWeb(TEST_DATA_DIR)
    bref = BaseballReference(web)
    assert bref.first_day(date(2023, 1, 1)) == date(2023, 3, 30)
