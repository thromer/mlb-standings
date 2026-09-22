"""Test updater.py"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, final
from zoneinfo import ZoneInfo

import pytest

import mlbstandings.updater
from mlbstandings.baseballref import PostSeason
from mlbstandings.helpers import date_from_excel_date, date_to_excel_date

from .fakes import FakeFiles, FakeSpreadsheets, FakeWeb
from .fixtures import TEST_DATA_DIR


if TYPE_CHECKING:
    import pathlib

    from mlbstandings.shared_types import SheetArray, SheetValue


CONTENTS_SHEET_ID = "contents"


def test_empty_unknown_opening_day() -> None:
    """Opening day unknown, don't do anything"""


@pytest.mark.datafiles(TEST_DATA_DIR / "test_empty_before_opening_day_spreadsheets")
def test_empty_before_opening_day(datafiles: pathlib.Path) -> None:
    """Opening day known (from schedule) so fill in openingDay-1 row"""
    for f in datafiles.iterdir():
        print(f.name)
    now = datetime(2023, 3, 30, tzinfo=ZoneInfo("America/Los_Angeles"))
    spreadsheets = FakeSpreadsheets(datafiles)
    files = FakeFiles()
    web = FakeWeb(TEST_DATA_DIR)
    try:
        updater = mlbstandings.updater.Updater(
            now,
            files,
            spreadsheets,
            CONTENTS_SHEET_ID,
            web,
            None,  # pyright: ignore[reportArgumentType]
        )
        _ = updater.update()
    finally:
        spreadsheets.close()
    spreadsheet = spreadsheets.spreadsheet(updater.get_spreadsheet_id_for_year(2023))
    first_day_val = spreadsheet.get_cell("first_day")
    if type(first_day_val) is not int:
        msg = f"{first_day_val} has type {type(first_day_val)}"
        raise TypeError(msg)
    print(f"first_day={date_from_excel_date(first_day_val)}")


# def test_empty_opening_day_done() -> None:
#     """Have data from first day"""
#     pass


def test_zero_row_opening_day_done() -> None:
    """Add data from first day"""


@pytest.mark.datafiles(TEST_DATA_DIR / "test_zero_row_multiple_days_done_spreadsheets")
def test_zero_row_multiple_days_done(datafiles: pathlib.Path) -> None:
    """Add data from multiple days"""
    now = datetime(2023, 5, 1, tzinfo=ZoneInfo("America/Los_Angeles"))
    spreadsheets = FakeSpreadsheets(datafiles)
    files = FakeFiles()
    web = FakeWeb(TEST_DATA_DIR)
    try:
        updater = mlbstandings.updater.Updater(
            now,
            files,
            spreadsheets,
            CONTENTS_SHEET_ID,
            web,
            None,  # pyright: ignore[reportArgumentType]
        )
        _ = updater.update()
    finally:
        spreadsheets.close()
    # TOOD get the data from the spreadsheet (or somewhere) and compare to expected
    # assert False


@final
class _DictSpreadsheet:
    """Minimal spreadsheet backed by a dict of named ranges."""

    def __init__(self, ranges: dict[str, SheetArray]) -> None:
        self.ranges = ranges

    def get_range(
        self,
        range_str: str,
        _major_dimension: str = "ROWS",
    ) -> SheetArray:
        return self.ranges.get(range_str, [[""]])

    def get_cell(self, cell_str: str) -> SheetValue:
        return self.get_range(cell_str)[0][0]

    def set_range(self, range_str: str, values: SheetArray) -> None:
        self.ranges[range_str] = values

    def set_cell(self, cell_str: str, value: SheetValue) -> None:
        self.set_range(cell_str, [[value]])


@final
class _DictSpreadsheets:
    def __init__(self, spreadsheets: dict[str, _DictSpreadsheet]) -> None:
        self.spreadsheets = spreadsheets

    def spreadsheet(self, spreadsheet_id: str) -> _DictSpreadsheet:
        return self.spreadsheets[spreadsheet_id]


@final
class _StubBaseballRef:
    def __init__(self, post_season: PostSeason) -> None:
        self.post_season = post_season

    def grab_post_season(self, _now: datetime) -> PostSeason:
        return self.post_season


def _post_season_updater(
    now: datetime, sheet_values: dict[str, SheetArray], post_season: PostSeason
) -> tuple[mlbstandings.updater.Updater, _DictSpreadsheet]:
    sheet = _DictSpreadsheet(sheet_values)
    contents = _DictSpreadsheet({"contents": [[now.year, "season"]]})
    spreadsheets = _DictSpreadsheets({CONTENTS_SHEET_ID: contents, "season": sheet})
    updater = mlbstandings.updater.Updater(
        now,
        FakeFiles(),
        spreadsheets,  # pyright: ignore[reportArgumentType]
        CONTENTS_SHEET_ID,
        FakeWeb(TEST_DATA_DIR),
        None,  # pyright: ignore[reportArgumentType]
    )
    updater.baseballref = _StubBaseballRef(post_season)  # pyright: ignore[reportAttributeAccessIssue]
    return updater, sheet


_POST_SEASON = PostSeason(
    "md5-1",
    ["description"],
    [["Wild Card Game 1"]],
    date(2025, 10, 5),
)


def test_post_season_unchanged_md5_mid_post_season_not_marked_over() -> None:
    """An unchanged md5 while in progress must not record last_post_season_day."""
    now = datetime(2025, 10, 3, 12, tzinfo=ZoneInfo("America/Los_Angeles"))
    updater, sheet = _post_season_updater(
        now, {"post_season_md5": [["md5-1"]]}, _POST_SEASON
    )
    assert updater.update_post_season() == mlbstandings.updater.SeasonStatus.IN_PROGRESS
    assert sheet.get_cell("last_post_season_day") == ""
    assert "playoff_upload!A:H" not in sheet.ranges


def test_post_season_changed_md5_mid_post_season_uploads() -> None:
    now = datetime(2025, 10, 3, 12, tzinfo=ZoneInfo("America/Los_Angeles"))
    updater, sheet = _post_season_updater(now, {}, _POST_SEASON)
    assert updater.update_post_season() == mlbstandings.updater.SeasonStatus.IN_PROGRESS
    assert sheet.get_range("playoff_upload!A:H") == [
        ["description"],
        ["Wild Card Game 1"],
    ]
    assert sheet.get_cell("post_season_md5") == "md5-1"
    assert sheet.get_cell("last_post_season_day") == ""


def test_post_season_unchanged_md5_after_post_season_marked_over() -> None:
    """Already uploaded but not yet marked done: mark it done."""
    now = datetime(2025, 10, 6, 12, tzinfo=ZoneInfo("America/Los_Angeles"))
    updater, sheet = _post_season_updater(
        now, {"post_season_md5": [["md5-1"]]}, _POST_SEASON
    )
    assert updater.update_post_season() == mlbstandings.updater.SeasonStatus.OVER
    assert sheet.get_cell("last_post_season_day") == date_to_excel_date(
        date(2025, 10, 5)
    )
    assert "playoff_upload!A:H" not in sheet.ranges


def test_post_season_after_gap_in_runs_keeps_updating() -> None:
    """A run after the schedule known at the previous run has passed still fetches."""
    now = datetime(2025, 10, 20, 12, tzinfo=ZoneInfo("America/Los_Angeles"))
    later = PostSeason(
        "md5-2",
        ["description"],
        [["Wild Card Game 1"], ["World Series Game 1"]],
        date(2025, 11, 1),
    )
    updater, sheet = _post_season_updater(now, {"post_season_md5": [["md5-1"]]}, later)
    assert updater.update_post_season() == mlbstandings.updater.SeasonStatus.IN_PROGRESS
    assert sheet.get_cell("post_season_md5") == "md5-2"
    assert sheet.get_cell("last_post_season_day") == ""
