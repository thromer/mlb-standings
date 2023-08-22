from datetime import timedelta, MINYEAR, MAXYEAR
# noinspection PyUnresolvedReferences
from datetime import date, datetime
from zoneinfo import ZoneInfo

from mlbstandings.baseballref import *
from mlbstandings.helpers import *
from mlbstandings.typing_protocols import *

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
_ONE_DAY = timedelta(days=1)
_LEAGUES = ['al', 'nl']

_MINDATE = date(MINYEAR, 1, 1)

# TODO inject rate limiter so that tests aren't limited?

class Updater:
    def __init__(self,
                 now: datetime,
                 drive: DriveLike,
                 spreadsheets: SpreadsheetsLike,
                 web: WebLike) -> None:
        if now.tzinfo is None or now.tzinfo.utcoffset(now) is None:
            raise ValueError("now should not be naive")
        self.now = now.astimezone(ZoneInfo('America/Los_Angeles'))  # TODO encapsulate day boundary logic somewheres
        self.drive = drive
        self.spreadsheets = spreadsheets
        # self.web = web
        self.baseballref = BaseballReference(web)

    @staticmethod
    def _spreadsheet_name(year: int) -> str:
        return f'MLB Standings {year}'

    @staticmethod
    def _upload_sheet_name(league: str) -> str:
        return f'{league}_uploaded'

    def update(self) -> None:
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
        # TODO catch FileNotFoundError and copy (to tmp name) & clear & rename
        spreadsheet_id = self.drive.get_spreadsheet_id(self._spreadsheet_name(self.now.year))
        spreadsheet = self.spreadsheets.spreadsheet(spreadsheet_id)

        first_day_val = spreadsheet.get_named_cell(_FIRST_DAY)
        if type(first_day_val) is int:
            first_day = date_from_excel_date(first_day_val)
        else:
            # TODO error handling
            first_day = self.baseballref.first_day(date(self.now.year, 1, 1))
            spreadsheet.set_named_cell(_FIRST_DAY, date_to_excel_date(first_day))
        newest_league_upload_day = {
            league: self._get_newest_league_day(spreadsheet, league) for league in _LEAGUES
        }
        first_day_to_upload = max(first_day - _ONE_DAY, min(newest_league_upload_day.values()) + _ONE_DAY)
        last_day_to_upload = date.fromordinal(self.now.toordinal()) - _ONE_DAY  # Ugly, assumes we already did the conversion to America/Los_Angeles
        # TODO test oround midnight boundary (assuming that's what we want)
        # if first_day_to_upload > today
        for day in [first_day_to_upload + timedelta(days=d)
                    for d in range((last_day_to_upload - first_day_to_upload).days + 1)]:
            if day == first_day - _ONE_DAY:
                rows = self.baseballref.zeroday()
            else:
                # TODO handle None
                rows = self.baseballref.something(day)
            print(rows)
        return

        # TODO handle -- and test -- case where each league has differrent newest day.
        last_day = date(MAXYEAR, 12, 31)
        for league in _LEAGUES:
            last_day = min(last_day, self._update_league(spreadsheet, first_day, league))
        if last_day >= date(self.now.year, 1, 1):
            spreadsheet.set_named_cell(_LAST_DAY, date_to_excel_date(last_day))

    def _get_newest_league_day(self, spreadsheet: SpreadsheetLike, league: str) -> date:
        column = spreadsheet.read_values(
            self._upload_sheet_name(league), 'A:A', major_dimension='COLUMNS')[0]
        if len(column) == 0:
            return _MINDATE
        cell = column[-1]
        if type(cell) is not int:
            return _MINDATE
        else:
            return date_from_excel_date(cell)

    def _update_league(self, spreadsheet: SpreadsheetLike, first_day: date, league: str) -> date:
        """Update league and returns last day of season if known, min day otherwise"""
        #     * Let spreadsheet_max_date = date of the latest spreadsheet row with data
        #     * Corner case: If there is *no* data in the spreadsheet, use opening day - 2.
        # TODO TODO TODO raise ValueError('implement me')

        return date(MINYEAR, 1, 1)
