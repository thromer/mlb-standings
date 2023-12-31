from datetime import timedelta, MINYEAR
from enum import Enum
from zoneinfo import ZoneInfo

from mlbstandings.baseballref import *
from mlbstandings.helpers import *
from mlbstandings.shared_types import *
from mlbstandings.typing_protocols import *

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from datetime import date, datetime
    from typing import Dict, List, Union

"""
Invariants:
* Spreadsheet rows are either complete for a date or empty
Loosely speaking:
* Run the following every hour, with
  * 'today' = yesterday, pacific time; so that starting at midnight PT, we
    see if we have all the results from yesterday if they're there.
"""

"""
* Supporting function: W-L as of date. We just use whatever baseball-reference tells us.
"""

_FIRST_DAY = 'first_day'
_LAST_DAY = 'last_day'
_POST_SEASON_MD5 = 'post_season_md5'
_LAST_POST_SEASON_DAY = 'last_post_season_day'
_ONE_DAY = timedelta(days=1)
_LEAGUES = ['AL', 'NL']

_MINDATE = date(MINYEAR, 1, 1)


class SeasonStatus(Enum):
    IN_PROGRESS = 1
    OVER = 2


class Updater:
    def __init__(self, now: datetime, spreadsheets: SpreadsheetsLike,
                 contents_id: str, web: WebLike) -> None:
        if now.tzinfo is None or now.tzinfo.utcoffset(now) is None:
            raise ValueError("now should not be naive")
        self.now = now.astimezone(ZoneInfo('America/Los_Angeles'))  # TODO encapsulate day boundary logic somewheres
        self.spreadsheets = spreadsheets
        self._contents = self._build_contents(spreadsheets.spreadsheet(contents_id))
        self.baseballref = BaseballReference(web)

    @staticmethod
    def _build_contents(contents_spreadsheet: SpreadsheetLike) -> Dict[int, str]:
        return {
            int(row[0]): str(row[1])
            for row in contents_spreadsheet.get_named_range('contents')
            if len(row) == 2 and type(row[0]) is int
        }

    @staticmethod
    def _spreadsheet_name(year: int) -> str:
        return f'MLB Standings {year}'

    @staticmethod
    def _upload_sheet_name(league: str) -> str:
        return f'{league.lower()}_uploaded'

    def get_spreadsheet_id_for_year(self, year: int) -> str:
        return str(self._contents[year])

    def update_regular_season(self) -> SeasonStatus:
        """
    * Corner case: For open day - 1, set everyone to 0
    * # Shortcut: If it is for today, we're done.
    * max_day = min('today', first day of post-season + a couple for buffer)
    * Backfill: for date in [spreadsheet_max_date + 1, 'today']
      * Are all games from date complete, one way or another?
        * Probably it suffices if baseball reference has published standings.
        * Future work: Special cases:
          * Rainouts
          * Suspended games -- I'm unclear on what this will look like on baseball-reference :(
            * Example: 2023-07-14 WSN vs STL
          * Doubleheaders
          * All-star break
          * Today: some games complete, some not
          * 1994: no post-season! Hard to see a solution besides a flag
            somewhere saying "last day of the season was X"
        * Good news: even if we handle a special case wrong, it'll get better the next day, probably.
    """
        first_day_val = self.spreadsheet.get_named_cell(_FIRST_DAY)
        if type(first_day_val) is int:
            first_day = date_from_excel_date(first_day_val)
        else:
            # TODO error handling
            first_day = self.baseballref.first_day(date(self.now.year, 1, 1))
            self.spreadsheet.set_named_cell(_FIRST_DAY, date_to_excel_date(first_day))
        last_day_val = self.spreadsheet.get_named_cell(_LAST_DAY)
        last_day = date_from_excel_date(last_day_val) if type(last_day_val) is int else None
        if last_day is not None:
            return SeasonStatus.OVER
        print(f'last_day before {last_day}')
        column_as = {
            league: self.spreadsheet.read_values(self._upload_sheet_name(league), 'A:A', major_dimension='COLUMNS')[0]
            for league in _LEAGUES
        }
        for league in _LEAGUES:
            # TODO this would be a nice time to make sure formatting for column A is correct
            if len(column_as[league]) == 0:
                row = self.baseballref.header_row(league)
                self.spreadsheet.write_values(
                    self._upload_sheet_name(league),
                    rc0_range_to_sheet_range(((0, 0), (0, len(row)))),
                    [[cast(SheetValue, 'Date')] + row])
        newest_league_upload_day = {
            league: self._get_newest_league_day(column_as[league], league, first_day)
            for league in _LEAGUES
        }
        first_day_to_upload = max(first_day - _ONE_DAY, min(newest_league_upload_day.values()) + _ONE_DAY)
        last_day_to_upload = date.fromordinal(self.now.toordinal()) - _ONE_DAY  # Ugly, assumes we already did the conversion to America/Los_Angeles
        if last_day is not None and last_day < last_day_to_upload:
            last_day_to_upload = last_day  # TODO seems unreachable since last_day is only set when the season is over anyway.
        # TODO test oround midnight boundary (assuming that's what we want)
        last_day_uploaded = None
        print(f'{first_day_to_upload=} {last_day_to_upload=}')
        for day in [first_day_to_upload + timedelta(days=d)
                    for d in range((last_day_to_upload - first_day_to_upload).days + 1)]:
            if day == first_day - _ONE_DAY:
                rows = self.baseballref.zeroday()
            else:
                rows = self.baseballref.spreadsheet_row(day)
            if rows is None:
                # TODO test this case
                break
            row_index = (day - first_day).days + 2
            for league in _LEAGUES:
                values = [date_to_excel_date(day)] + rows[league]
                sheet_range = rc0_range_to_sheet_range(((row_index, 0), (row_index, len(values) - 1)))
                self.spreadsheet.write_values(self._upload_sheet_name(league), sheet_range, [values])
            last_day_uploaded = day
        print(f'{last_day_uploaded=}')

        # If we didn't upload anything on the last iteration it might be that we're at the end of the season.
        # TODO This misses backfill case the first time around but I don't think I care that much.
        if last_day is None and last_day_uploaded != last_day_to_upload:
            last_day = self.baseballref.last_scheduled_regular_day(min(newest_league_upload_day.values()))
            if last_day < self.now.date():
                print('update _LAST_DAY')
                self.spreadsheet.set_named_cell(_LAST_DAY, date_to_excel_date(last_day))
                return SeasonStatus.OVER

        return SeasonStatus.IN_PROGRESS

        # preferably nothing left to do esp b/c break statement
        # TODO what about last_day ?

        # # TODO handle -- and test -- case where each league has different newest day.
        # last_day = date(MAXYEAR, 12, 31)
        # for league in _LEAGUES:
        #     last_day = min(last_day, self._update_league(spreadsheet, first_day, league))
        # if last_day >= date(self.now.year, 1, 1):
        #     spreadsheet.set_named_cell(_LAST_DAY, date_to_excel_date(last_day))

    def update_post_season(self) -> SeasonStatus:
        # TODO I don't think this is quite robust but ok.
        last_post_season_day_val = self.spreadsheet.get_named_cell(_LAST_POST_SEASON_DAY)
        last_post_season_day = date_from_excel_date(last_post_season_day_val) if type(last_post_season_day_val) is int else None
        if last_post_season_day is not None and last_post_season_day < self.now.date():
            return SeasonStatus.OVER
        post_season = self.baseballref.grab_post_season(self.now)
        previous_md5 = self.spreadsheet.get_named_cell(_POST_SEASON_MD5)
        in_progress = post_season['last_scheduled_day'] >= self.now.date()
        result = SeasonStatus.IN_PROGRESS if in_progress else SeasonStatus.OVER
        if post_season['md5'] == previous_md5:
            # ugh
            self.spreadsheet.set_named_cell(_LAST_POST_SEASON_DAY, date_to_excel_date(
                post_season['last_scheduled_day']))
            return result
        table = [post_season['header']] + post_season['rows']
        self.spreadsheet.write_values('playoff_upload','A:H',table)
        if not in_progress:
            self.spreadsheet.set_named_cell(_LAST_POST_SEASON_DAY, date_to_excel_date(
                post_season['last_scheduled_day']))
        self.spreadsheet.set_named_cell(_POST_SEASON_MD5, post_season['md5'])
        return result

    def update(self) -> SeasonStatus:
        # TODO catch FileNotFoundError and copy (to tmp name) & clear & rename
        spreadsheet_id = self.get_spreadsheet_id_for_year(self.now.year)
        self.spreadsheet = self.spreadsheets.spreadsheet(spreadsheet_id)
        if self.update_regular_season() == SeasonStatus.IN_PROGRESS:
            return SeasonStatus.IN_PROGRESS
        return self.update_post_season()

    def _get_newest_league_day(self, column: List[SheetValue], league: str, first_day: date) -> date:
        if len(column) <= 1:
            return _MINDATE
        # Check that values sequentially increase starting with first_day - 1
        want = first_day - _ONE_DAY
        for sheet_val in column[1:]:
            if type(sheet_val) != int:
                raise ValueError(f'Unexpected value {sheet_val} in column A2:A')
            got = date_from_excel_date(sheet_val)
            if type(sheet_val) != int or got != want:
                raise ValueError(f'Expected date {want} in {self._upload_sheet_name(league)} but got {got}')
            want = want + _ONE_DAY

        cell = column[-1]
        if type(cell) is not int:
            return _MINDATE
        else:
            return date_from_excel_date(cell)
