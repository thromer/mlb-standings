import os
import pytest
from _pytest.nodes import Node

from fakes import FakeWeb
from mlbstandings.baseballref import BaseballReference

from datetime import datetime


@pytest.fixture
def testdatadir(request: Node) -> str:
    return os.path.join(request.fspath.dirname, "../test-data")


def test_opening_day(testdatadir: str) -> None:
    web = FakeWeb(testdatadir)
    bref = BaseballReference(web)
    assert bref.opening_day(datetime(2023, 1, 1)) == datetime(2023, 3, 30)
