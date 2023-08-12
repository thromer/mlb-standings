#!/usr/bin/env python3

"""
Invariants:
* Spreadsheet rows are either complete for a date or empty.

Loosely speaking:
* Let spreadsheet_max_date = date of the latest spreadsheet row with data
* Corner case: If there is *no* data in the spreadsheet, use opening day - 1.
* # Shortcut: If it is for today, we're done.
* Backfill: for date = spreadsheet_max_date + 1 through today
  * Are all games from date complete, one way or another?
    * Special cases:
      * Rainouts
      * Suspended games -- I'm unclear on what this will look like on baseball-reference :(
        * Example: 2023-07-14 WSN vs STL
      * Doubleheaders
      * All-star break
      * Today: some games complete, some not
    * Good news: even if we handle a special case wrong, it'll get better the next day, probably.

* Supporting function: W-L as of date. We just use whatever baseball-reference tells us.
"""
