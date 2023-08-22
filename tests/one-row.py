#!/usr/bin/env python3
from datetime import date
from mlbstandings.baseballref import BaseballReference
from fakes import FakeWeb
from fixtures import testdatadir


def test_main(testdatadir: str) -> None:
    br = BaseballReference(FakeWeb(testdatadir))
    print(f'first_day={br.first_day(date(2023, 1, 1))}')
    print(br.something(date(2023, 4, 15)))
