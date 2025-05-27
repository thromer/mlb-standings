import flask
import functions_framework

import email
import google.auth
import logging
import smtplib

# TODO figure out haw to import these nicely and still have mypy work.
import mlbstandings.light_google_wrappers
import mlbstandings.updater
import mlbstandings.web

from datetime import datetime
from zoneinfo import ZoneInfo
from google.auth.transport.requests import AuthorizedSession
from google.cloud import secretmanager
# from googleapiclient.discovery import build
from mlbstandings.abstract_rate_limited_web import AbstractRateLimitedWeb
from mlbstandings.rate_limiter import SimpleRateLimiter
from typing import Optional, cast

GMAIL_SMTP_SECRET_NAME = 'projects/mlb-standings-001/secrets/gmail-smtp/versions/latest'

logging.getLogger('backoff').addHandler(logging.StreamHandler())

@functions_framework.http
def cf_test(request: Optional[flask.Request], args: list[str]=[]) -> str:
    print(type(request))
    if isinstance(request, flask.Request):
        request_json = request.get_json(silent=True)
        request_args = request.args
        print(f'{request_json=}')
        print(f'{request_args=}')
    # More scopes? Re-run gcloud auth application-default login
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = google.auth.default(scopes=scopes)[0]  # type: ignore
    authed_session = AuthorizedSession(creds)  # type: ignore
    sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
    spreadsheet = sheets.spreadsheet('1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo')
    before = spreadsheet.get_range('Sheet1!A6:A6')
    old_val = before[0][0]
    new_val = 0 if type(old_val) is str else cast(int, old_val) + 1
    print(f"Before {before}")
    spreadsheet.set_range('Sheet1!A6:A6', [[new_val]])
    print(f"After {spreadsheet.get_range('Sheet1!A6:A6')}")

    return str(new_val)


# @functions_framework.http
# def spreadsheetCopy(request: Optional[flask.Request], args=[]) -> str:
#     # More scopes? Re-run gcloud auth application-default login
#     scopes = ['https://www.googleapis.com/auth/drive',  # to create spreadsheets
#               'https://www.googleapis.com/auth/spreadsheets',
#               'https://www.googleapis.com/auth/drive.metadata.readonly']
#     creds = google.auth.default(scopes=scopes)[0]
#     files = build('drive','v3',credentials=creds).files()
#     oldId='14h3hTCvXNzUqTtbegIzSE6JwetMgvtWB6xP9gv87gZs'
#     files.copy(fileId=oldId).execute()
#     return 'Done'


CONTENTS_SPREADSHEET_ID = '1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo'


@functions_framework.http
def update(_: Optional[flask.Request], args: list[str]=[]) -> str:
    backfill = False
    if len(args) > 0:
        d = datetime(int(args[0]), 12, 31, 0, 0, 0, 0, ZoneInfo('Etc/UTC'))
        backfill = True
    else:
        d = datetime.now(tz=ZoneInfo('Etc/UTC'))
    # More scopes? Re-run gcloud auth application-default login.
    # But not working locally :(
    # How did I update scopes for the cloud function esp auth/drive ?
    scopes = ['https://www.googleapis.com/auth/drive',  # to create spreadsheets
              'https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive.metadata.readonly']  # unlikely we need this?
    creds = google.auth.default(scopes=scopes)[0]  # type: ignore
    authed_session = AuthorizedSession(creds)  # type: ignore
    files = mlbstandings.light_google_wrappers.Files(authed_session)
    sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
    base_web = mlbstandings.web.Web()
    web = AbstractRateLimitedWeb(base_web, SimpleRateLimiter(15))
    updater = mlbstandings.updater.Updater(d, files, sheets, CONTENTS_SPREADSHEET_ID, web)
    # TODO remove once everything works with new versions
    base_web.read('https://www.baseball-reference.com/')
    print('No problem reading www.baseball-reference.com')
    while True:
        status = updater.update()
        if status == None or status == mlbstandings.updater.SeasonStatus.OVER or not backfill:
            break
    return 'Done'


def mailtest(_: Optional[flask.Request], args:list[str]=[]) -> str:
    msg = email.message.EmailMessage()
    url = f'https://docs.google.com/spreadsheets/d/1_alHZscHsxiKi3Zp90wuSpJEqoAcrhBPQ9LRTytWgy4/edit'
    name = 'MLB Standings 2024'
    html_content = '''<html>
  <head></head>
  <body>
    <p>See <a href="%s"> %s</a>.</p>
  </body>
</html>''' % (url, name)
    print(html_content)
    msg.set_content(f'See {url}')
    msg.add_alternative(html_content, subtype='html')
    msg['Subject'] = 'subject local'
    msg['From'] = 'tromer@gmail.com'
    msg['To'] = 'tromer@gmail.com'
    secret_manager_client = secretmanager.SecretManagerServiceClient()
    # Has retry built-in.
    password = secret_manager_client.access_secret_version(
        request={'name': GMAIL_SMTP_SECRET_NAME}).payload.data.decode()
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('tromer@gmail.com', password)
        smtp.send_message(msg)
    return 'Done'
