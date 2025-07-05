import flask
from flask.typing import ResponseReturnValue

import google.auth
import logging

# TODO figure out how to import these nicely and still have mypy work.
from . import light_google_wrappers, updater, web

from datetime import datetime
from zoneinfo import ZoneInfo
from google.auth.transport.requests import AuthorizedSession
# from googleapiclient.discovery import build
from .abstract_rate_limited_web import AbstractRateLimitedWeb
from .rate_limiter import SimpleRateLimiter


logging.getLogger('backoff').addHandler(logging.StreamHandler())
app = flask.Flask(__name__)

CONTENTS_SPREADSHEET_ID = '1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo'


@app.route('/', methods=['GET', 'POST'])
def update() -> ResponseReturnValue:
    backfill = False
#    if len(args) > 0:
#        d = datetime(int(args[0]), 12, 31, 0, 0, 0, 0, ZoneInfo('Etc/UTC'))
#        backfill = True
#    else:
    d = datetime.now(tz=ZoneInfo('Etc/UTC'))
    # More scopes? Re-run gcloud auth application-default login.
    # But not working locally :(
    # How did I update scopes for the cloud function esp auth/drive ?
    scopes = ['https://www.googleapis.com/auth/drive',  # to create spreadsheets
              'https://www.googleapis.com/auth/spreadsheets']
    creds = google.auth.default(scopes=scopes)[0]  # type: ignore
    authed_session = AuthorizedSession(creds)  # type: ignore
    files = light_google_wrappers.Files(authed_session)
    sheets = light_google_wrappers.Spreadsheets(authed_session)
    base_web = web.Web()
    w = AbstractRateLimitedWeb(base_web, SimpleRateLimiter(15))
    u = updater.Updater(d, files, sheets, CONTENTS_SPREADSHEET_ID, w)
    while True:
        status = u.update()
        if status is None or status == updater.SeasonStatus.OVER or not backfill:
            break
    return 'Done\n'
