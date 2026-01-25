import email.message
import logging
import smtplib

# from googleapiclient.discovery import build
from typing import cast

import flask
import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.cloud.secretmanager import SecretManagerServiceClient

import mlbstandings.light_google_wrappers


GMAIL_SMTP_SECRET_NAME = "projects/mlb-standings-001/secrets/gmail-smtp/versions/latest"

logging.getLogger("backoff").addHandler(logging.StreamHandler())

# TODO: Handle more than one function maybe.
app = flask.Flask(__name__)


def cf_test(request: flask.Request | None, _) -> str:
    print(type(request))
    if isinstance(request, flask.Request):
        request_json = request.get_json(silent=True)
        request_args = request.args
        print(f"{request_json=}")
        print(f"{request_args=}")
    # More scopes? Re-run gcloud auth application-default login
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    creds = google.auth.default(scopes=scopes)[0]  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    authed_session = AuthorizedSession(creds)  # pyright: ignore[reportUnknownArgumentType]
    sheets = mlbstandings.light_google_wrappers.Spreadsheets(authed_session)
    spreadsheet = sheets.spreadsheet("1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo")
    before = spreadsheet.get_range("Sheet1!A6:A6")
    old_val = before[0][0]
    new_val = 0 if type(old_val) is str else cast(int, old_val) + 1
    print(f"Before {before}")
    spreadsheet.set_range("Sheet1!A6:A6", [[new_val]])
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
#     return 'Done\n'


def mailtest(_req: flask.Request | None) -> str:
    msg = email.message.EmailMessage()
    url = "https://docs.google.com/spreadsheets/d/1_alHZscHsxiKi3Zp90wuSpJEqoAcrhBPQ9LRTytWgy4/edit"
    name = "MLB Standings 2024"
    html_content = """<html>
  <head></head>
  <body>
    <p>See <a href="%s"> %s</a>.</p>
  </body>
</html>""" % (url, name)
    print(html_content)
    msg.set_content(f"See {url}")
    msg.add_alternative(html_content, subtype="html")
    msg["Subject"] = "subject local"
    msg["From"] = "tromer@gmail.com"
    msg["To"] = "tromer@gmail.com"
    secret_manager_client = SecretManagerServiceClient()
    # Has retry built-in.
    password = secret_manager_client.access_secret_version(  # pyright: ignore[reportUnknownMemberType]
        request={"name": GMAIL_SMTP_SECRET_NAME}
    ).payload.data.decode()
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        _ = smtp.ehlo()
        _ = smtp.starttls()
        _ = smtp.login("tromer@gmail.com", password)
        _ = smtp.send_message(msg)
    return "Done\n"
