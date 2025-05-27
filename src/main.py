import flask
import requests

#repro0 import email
#repro1 import google.auth
#repro0 import logging
#repro0 import smtplib

# TODO figure out how to import these nicely and still have mypy work.
#repro0 import mlbstandings.light_google_wrappers
#repro0 import mlbstandings.updater
#repro3 import mlbstandings.web

#repro3 from datetime import datetime
#repro3 from zoneinfo import ZoneInfo
#repro0 from google.auth.transport.requests import AuthorizedSession
#repro0 from google.cloud import secretmanager
# from googleapiclient.discovery import build
#repro0 from mlbstandings.abstract_rate_limited_web import AbstractRateLimitedWeb
#repro0 from mlbstandings.rate_limiter import SimpleRateLimiter
#repro3 from typing import Optional, cast

#repro3 GMAIL_SMTP_SECRET_NAME = 'projects/mlb-standings-001/secrets/gmail-smtp/versions/latest'

#repro0 logging.getLogger('backoff').addHandler(logging.StreamHandler())

# TODO Handle more than one function maybe.
app = flask.Flask(__name__)

#repro0 def cf_test(request: Optional[flask.Request], args=[]) -> str:
#repro0     print(type(request))
#repro0     if isinstance(request, flask.Request):
#repro0         request_json = request.get_json(silent=True)
#repro0         request_args = request.args
#repro0         print(f'{request_json=}')
#repro0         print(f'{request_args=}')
#repro0     # More scopes? Re-run gcloud auth application-default login
#repro0     scopes = ['https://www.googleapis.com/auth/spreadsheets']
#repro0     creds = google.auth.default(scopes=scopes)[0]  # type: ignore
#repro0     authed_session = AuthorizedSession(creds)  # type: ignore
#repro0     sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
#repro0     spreadsheet = sheets.spreadsheet('1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo')
#repro0     before = spreadsheet.get_range('Sheet1!A6:A6')
#repro0     old_val = before[0][0]
#repro0     new_val = 0 if type(old_val) is str else cast(int, old_val) + 1
#repro0     print(f"Before {before}")
#repro0     spreadsheet.set_range('Sheet1!A6:A6', [[new_val]])
#repro0     print(f"After {spreadsheet.get_range('Sheet1!A6:A6')}")
#repro0 
#repro0     return str(new_val)


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


#repro3 CONTENTS_SPREADSHEET_ID = '1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo'


@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def update(path=''):
#repro3    backfill = False
#    if len(args) > 0:
#        d = datetime(int(args[0]), 12, 31, 0, 0, 0, 0, ZoneInfo('Etc/UTC'))
#        backfill = True
#    else:
#repro3    d = datetime.now(tz=ZoneInfo('Etc/UTC'))
    # More scopes? Re-run gcloud auth application-default login.
    # But not working locally :(
    # How did I update scopes for the cloud function esp auth/drive ?
#repro3     scopes = ['https://www.googleapis.com/auth/drive',  # to create spreadsheets
#repro3               'https://www.googleapis.com/auth/spreadsheets',
#repro3               'https://www.googleapis.com/auth/drive.metadata.readonly']  # unlikely we need this?
#repro0     creds = google.auth.default(scopes=scopes)[0]  # type: ignore
#repro0     authed_session = AuthorizedSession(creds)  # type: ignore
#repro0     files = mlbstandings.light_google_wrappers.Files(authed_session)
#repro0     sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
#repro3     base_web = mlbstandings.web.Web()
#repro0     web = AbstractRateLimitedWeb(base_web, SimpleRateLimiter(15))
#repro0     updater = mlbstandings.updater.Updater(d, files, sheets, CONTENTS_SPREADSHEET_ID, web)
    # TODO remove once everything works with new versions
    r = requests.get('https://www.baseball-reference.com/')
    r.raise_for_status()
#repro3     base_web.read('https://www.baseball-reference.com/')
    print('No problem reading www.baseball-reference.com')
#repro0     while True:
#repro0         status = updater.update()
#repro0         if status == None or status == mlbstandings.updater.SeasonStatus.OVER or not backfill:
#repro0             break
    return 'Done\n'


#repro0 def mailtest(_: Optional[flask.Request], args:list[str]=[]) -> str:
#repro0     msg = email.message.EmailMessage()
#repro0     url = f'https://docs.google.com/spreadsheets/d/1_alHZscHsxiKi3Zp90wuSpJEqoAcrhBPQ9LRTytWgy4/edit'
#repro0     name = 'MLB Standings 2024'
#repro0     html_content = '''<html>
#repro0   <head></head>
#repro0   <body>
#repro0     <p>See <a href="%s"> %s</a>.</p>
#repro0   </body>
#repro0 </html>''' % (url, name)
#repro0     print(html_content)
#repro0     msg.set_content(f'See {url}')
#repro0     msg.add_alternative(html_content, subtype='html')
#repro0     msg['Subject'] = 'subject local'
#repro0     msg['From'] = 'tromer@gmail.com'
#repro0     msg['To'] = 'tromer@gmail.com'
#repro0     secret_manager_client = secretmanager.SecretManagerServiceClient()
#repro0     # Has retry built-in.
#repro0     password = secret_manager_client.access_secret_version(
#repro0         request={'name': GMAIL_SMTP_SECRET_NAME}).payload.data.decode()
#repro0     with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#repro0         smtp.ehlo()
#repro0         smtp.starttls()
#repro0         smtp.login('tromer@gmail.com', password)
#repro0         smtp.send_message(msg)
#repro0     return 'Done\n'
