import os
import pytest

from fakes import FakeWeb
from mlbstandings.baseballref import BaseballReference

from datetime import datetime


@pytest.fixture
def testdatadir(request):
    return os.path.join(request.fspath.dirname, "../test-data")


def test_opening_day(testdatadir) -> None:
    web = FakeWeb(testdatadir)
    bref = BaseballReference(web)
    assert bref.opening_day(datetime(2023, 1, 1)) == datetime(2023, 3, 30)
