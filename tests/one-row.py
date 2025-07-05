#!/usr/bin/env python3
from datetime import date

from fakes import FakeWeb
from fixtures import TEST_DATA_DIR

from mlbstandings.baseballref import BaseballReference


def test_main() -> None:
    br = BaseballReference(FakeWeb(TEST_DATA_DIR))
    print(f'first_day={br.first_day(date(2023, 1, 1))}')
    print(br.spreadsheet_row(date(2023, 4, 15)))
