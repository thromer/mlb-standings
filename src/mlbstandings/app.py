import json
import logging
import sys
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import flask
import google.auth
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials


if TYPE_CHECKING:
    from flask.typing import ResponseReturnValue

    from mlbstandings.typing_protocols import SpreadsheetsLike

# TODO: figure out how to import these nicely and still have mypy work.
from . import light_google_wrappers, updater, web

# from googleapiclient.discovery import build
from .abstract_rate_limited_web import AbstractRateLimitedWeb
from .rate_limiter import SimpleRateLimiter


logging.getLogger("backoff").addHandler(logging.StreamHandler())
app = flask.Flask(__name__)

CONTENTS_SPREADSHEET_ID = "1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo"

# TODO: get these from constants.py
PROJECT_ID = "mlb-standings-001"
SECRET_ID = "creds"
SCOPES = [
    "https://www.googleapis.com/auth/drive",  # Need broad scope to copy
    "https://www.googleapis.com/auth/spreadsheets",
]


def run_update(backfill_year: int | None) -> None:
    backfill = backfill_year is not None
    if backfill_year is not None:
        d = datetime(backfill_year, 12, 31, tzinfo=ZoneInfo("Etc/UTC"))
    else:
        d = datetime.now(tz=ZoneInfo("Etc/UTC"))
    secrets = light_google_wrappers.Secrets(
        AuthorizedSession(google.auth.default()[0]),  # pyright:ignore[reportUnknownMemberType,reportUnknownArgumentType]
        PROJECT_ID,
    )
    creds_data = json.loads(secrets.access_secret_version(SECRET_ID))  # pyright:ignore[reportAny]
    installed = creds_data["installed_secret"]  # pyright:ignore[reportAny]
    creds = Credentials(
        None,
        refresh_token=creds_data["refresh_token"],  # pyright:ignore[reportAny]
        token_uri=installed["token_uri"],  # pyright:ignore[reportAny]
        client_id=installed["client_id"],  # pyright:ignore[reportAny]
        client_secret=installed["client_secret"],  # pyright:ignore[reportAny]
    )
    authed_session = AuthorizedSession(creds)
    files = light_google_wrappers.Files(authed_session)
    sheets: SpreadsheetsLike = light_google_wrappers.Spreadsheets(authed_session)
    base_web = web.Web()
    w = AbstractRateLimitedWeb(base_web, SimpleRateLimiter(15))
    u = updater.Updater(d, files, sheets, CONTENTS_SPREADSHEET_ID, w, secrets)
    while True:
        status = u.update()
        if status is None or status == updater.SeasonStatus.OVER or not backfill:
            break


@app.route("/", methods=["GET", "POST"])
def update() -> ResponseReturnValue:
    run_update(None)
    return "Done\n"


def main() -> None:
    run_update(int(sys.argv[1]) if len(sys.argv) >= 2 else None)
