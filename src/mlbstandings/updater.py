from datetime import datetime

from mlbstandings.typing_protocols import *

"""
Invariants:
* Spreadsheet rows are either complete for a date or empty.

Loosely speaking:
* Run the following every hour, with
  * 'today' = yesterday, pacific time; so that starting at midnight PT, we
    see if we have all the results from yesterday if they're there.
"""

"""
* Supporting function: W-L as of date. We just use whatever baseball-reference tells us.
"""

# TODO inject rate limiter so that tests aren't limited?
class Updater:
  def __init__(self, 
               now: datetime, 
               drive: DriveLike, 
               web: WebLike) -> None:
    self.now = now
    self.drive = drive
    self.web = web

  def update(self) -> None:
    """
    * Let spreadsheet_max_date = date of the latest spreadsheet row with data
    * Corner case: If there is *no* data in the spreadsheet, use opening day - 1.
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
    pass