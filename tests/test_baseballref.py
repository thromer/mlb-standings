from datetime import date
from typing import List, Dict, cast

from fakes import FakeWeb
from fixtures import TEST_DATA_DIR
from mlbstandings.baseballref import BaseballReference
from mlbstandings.shared_types import SheetValue


def test_first_day() -> None:
    web = FakeWeb(TEST_DATA_DIR)
    bref = BaseballReference(web)
    assert bref.first_day(date(2023, 1, 1)) == date(2023, 3, 30)


def test_later_day() -> None:
    web = FakeWeb(TEST_DATA_DIR)
    bref = BaseballReference(web)
    headers: Dict[str, List[SheetValue]] = {
        league: bref.header_row(league)
        for league in ['AL', 'NL']
    }
    result = bref.spreadsheet_row(date(2023, 4, 30))
    if result is None:
        raise ValueError('None')
    result = cast(dict[str, list[SheetValue]], result)
    # print(headers)
    # print(result)
    # for league in ['AL', 'NL']:
    #     print(f'\n\n{league}')
    #     indices = {
    #         headers[league][i]: i
    #         for i in range(15)
    #     }
    #     for r in [
    #         [15, 20],
    #         [20, 25],
    #         [25, 30],
    #         [30, len(result[league])]
    #     ]:
    #         for i in range(r[0], r[1]):
    #             abbr = result[league][i]
    #             print(f'{i} {abbr} {result[league][indices[abbr]]}')
    #         print()
