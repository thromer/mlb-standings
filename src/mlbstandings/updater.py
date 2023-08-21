from datetime import MAXYEAR
# noinspection PyUnresolvedReferences
from datetime import date, datetime

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

FIRST_DAY = 'first_day'
LAST_DAY = 'last_day'

LEAGUES = ['al', 'nl']


# TODO inject rate limiter so that tests aren't limited?
class Updater:
    def __init__(self,
                 now: datetime,
                 drive: DriveLike,
                 spreadsheets: SpreadsheetsLike,
                 web: WebLike) -> None:
        self.now = now
        self.drive = drive
        self.spreadsheets = spreadsheets
        # self.web = web
        self.baseballref = BaseballReference(web)

    @staticmethod
    def _spreadsheet_name(year: int) -> str:
        return f'MLB Standings {year}'

    def update(self) -> None:
        """
    * and by the way persist opening day and ending day somewhere (once they are known)

    * Let spreadsheet_max_date = date of the latest spreadsheet row with data
    * Corner case: If there is *no* data in the spreadsheet, use opening day - 2.
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
        # TODO make this into a datetime please!
        #
        first_day_val = spreadsheet.get_named_cell(FIRST_DAY)
        if type(first_day_val) is int:
            first_day = date_from_excel_date(first_day_val)
        else:
            # TODO error handling
            first_day = self.baseballref.first_day(date(self.now.year, 1, 1))
            spreadsheet.set_named_cell(FIRST_DAY, date_to_excel_date(first_day))
        last_day = date(MAXYEAR, 12, 31)
        for league in LEAGUES:
            last_day = min(last_day, self._update_league(spreadsheet, first_day, league))
        if last_day >= date(self.now.year, 1, 1):
            spreadsheet.set_named_cell(LAST_DAY, date_to_excel_date(last_day))

    def _update_league(self, spreadsheet: SpreadsheetLike, first_day: date, league: str) -> date:
        raise ValueError('implement me')
