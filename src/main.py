import flask
import functions_framework

import google.auth
# TODO figure out haw to import these nicely and still have mypy work.
import mlbstandings.google_wrappers
import mlbstandings.updater
import mlbstandings.web

from datetime import datetime
from zoneinfo import ZoneInfo
from mlbstandings.abstract_rate_limited_web import AbstractRateLimitedWeb
from mlbstandings.rate_limiter import SimpleRateLimiter
from typing import Optional, cast


@functions_framework.http
def cf_test(request: Optional[flask.Request], args=[]) -> str:
    print(type(request))
    if isinstance(request, flask.Request):
        request_json = request.get_json(silent=True)
        request_args = request.args
        print(f'{request_json=}')
        print(f'{request_args=}')
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = google.auth.default(scopes=scopes)[0]
    sheets = mlbstandings.google_wrappers.Spreadsheets(creds)
    spreadsheet = sheets.spreadsheet('1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo')
    before = spreadsheet.read_values('Sheet1', 'A6:A6')
    old_val = before[0][0]
    new_val = 0 if type(old_val) is str else cast(int, old_val) + 1
    print(f"Before {before}")
    spreadsheet.write_values('Sheet1', 'A6:A6', [[new_val]])
    print(f"After {spreadsheet.read_values('Sheet1', 'A6:A6')}")

    return str(new_val)


CONTENTS_SPREADSHEET_ID = '1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo'


@functions_framework.http
def update(_: Optional[flask.Request], args=[]) -> str:
    backfill = False
    if len(args) > 0:
        d = datetime(int(args[0]), 12, 31, 0, 0, 0, 0, ZoneInfo('Etc/UTC'))
        backfill = True
    else:
        d = datetime.now(tz=ZoneInfo('Etc/UTC'))
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive.metadata.readonly']
    creds = google.auth.default(scopes=scopes)[0]
    sheets = mlbstandings.google_wrappers.Spreadsheets(creds)
    base_web = mlbstandings.web.Web()
    web = AbstractRateLimitedWeb(base_web, SimpleRateLimiter(15))
    updater = mlbstandings.updater.Updater(d, sheets, CONTENTS_SPREADSHEET_ID, web)
    while True:
        status = updater.update()
        if status == mlbstandings.updater.SeasonStatus.OVER or not backfill:
            break
    return 'Done'
