import flask

#repro import email
import google.auth
#repro import logging
#repro import smtplib

# TODO figure out how to import these nicely and still have mypy work.
#repro import mlbstandings.light_google_wrappers
#repro import mlbstandings.updater
import mlbstandings.web

from datetime import datetime
from zoneinfo import ZoneInfo
#repro from google.auth.transport.requests import AuthorizedSession
#repro from google.cloud import secretmanager
# from googleapiclient.discovery import build
#repro from mlbstandings.abstract_rate_limited_web import AbstractRateLimitedWeb
#repro from mlbstandings.rate_limiter import SimpleRateLimiter
from typing import Optional, cast

GMAIL_SMTP_SECRET_NAME = 'projects/mlb-standings-001/secrets/gmail-smtp/versions/latest'

#repro logging.getLogger('backoff').addHandler(logging.StreamHandler())

# TODO Handle more than one function maybe.
app = flask.Flask(__name__)

#repro def cf_test(request: Optional[flask.Request], args=[]) -> str:
#repro     print(type(request))
#repro     if isinstance(request, flask.Request):
#repro         request_json = request.get_json(silent=True)
#repro         request_args = request.args
#repro         print(f'{request_json=}')
#repro         print(f'{request_args=}')
#repro     # More scopes? Re-run gcloud auth application-default login
#repro     scopes = ['https://www.googleapis.com/auth/spreadsheets']
#repro     creds = google.auth.default(scopes=scopes)[0]  # type: ignore
#repro     authed_session = AuthorizedSession(creds)  # type: ignore
#repro     sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
#repro     spreadsheet = sheets.spreadsheet('1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo')
#repro     before = spreadsheet.get_range('Sheet1!A6:A6')
#repro     old_val = before[0][0]
#repro     new_val = 0 if type(old_val) is str else cast(int, old_val) + 1
#repro     print(f"Before {before}")
#repro     spreadsheet.set_range('Sheet1!A6:A6', [[new_val]])
#repro     print(f"After {spreadsheet.get_range('Sheet1!A6:A6')}")
#repro 
#repro     return str(new_val)


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
#     return 'Done\n'


CONTENTS_SPREADSHEET_ID = '1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo'


@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def update(path=''):
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
              'https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive.metadata.readonly']  # unlikely we need this?
#repro     creds = google.auth.default(scopes=scopes)[0]  # type: ignore
#repro     authed_session = AuthorizedSession(creds)  # type: ignore
#repro     files = mlbstandings.light_google_wrappers.Files(authed_session)
#repro     sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
    base_web = mlbstandings.web.Web()
#repro     web = AbstractRateLimitedWeb(base_web, SimpleRateLimiter(15))
#repro     updater = mlbstandings.updater.Updater(d, files, sheets, CONTENTS_SPREADSHEET_ID, web)
    # TODO remove once everything works with new versions
    base_web.read('https://www.baseball-reference.com/')
    print('No problem reading www.baseball-reference.com')
#repro     while True:
#repro         status = updater.update()
#repro         if status == None or status == mlbstandings.updater.SeasonStatus.OVER or not backfill:
#repro             break
    return 'Done\n'


#repro def mailtest(_: Optional[flask.Request], args:list[str]=[]) -> str:
#repro     msg = email.message.EmailMessage()
#repro     url = f'https://docs.google.com/spreadsheets/d/1_alHZscHsxiKi3Zp90wuSpJEqoAcrhBPQ9LRTytWgy4/edit'
#repro     name = 'MLB Standings 2024'
#repro     html_content = '''<html>
#repro   <head></head>
#repro   <body>
#repro     <p>See <a href="%s"> %s</a>.</p>
#repro   </body>
#repro </html>''' % (url, name)
#repro     print(html_content)
#repro     msg.set_content(f'See {url}')
#repro     msg.add_alternative(html_content, subtype='html')
#repro     msg['Subject'] = 'subject local'
#repro     msg['From'] = 'tromer@gmail.com'
#repro     msg['To'] = 'tromer@gmail.com'
#repro     secret_manager_client = secretmanager.SecretManagerServiceClient()
#repro     # Has retry built-in.
#repro     password = secret_manager_client.access_secret_version(
#repro         request={'name': GMAIL_SMTP_SECRET_NAME}).payload.data.decode()
#repro     with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#repro         smtp.ehlo()
#repro         smtp.starttls()
#repro         smtp.login('tromer@gmail.com', password)
#repro         smtp.send_message(msg)
#repro     return 'Done\n'
