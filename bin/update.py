#!/usr/bin/env python3
from zoneinfo import ZoneInfo

import google.auth

from datetime import datetime

# TODO figure out haw to import these nicely and still have mypy work.
import mlbstandings.google_wrappers
import mlbstandings.updater
import mlbstandings.web


def main() -> None:
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive.metadata.readonly']
    creds = google.auth.default(scopes=scopes)[0]
    drive = mlbstandings.google_wrappers.Drive(creds)
    sheets = mlbstandings.google_wrappers.Spreadsheets(creds)
    updater = mlbstandings.updater.Updater(datetime.now(tz=ZoneInfo('Etc/UTC')), drive, sheets, mlbstandings.web.Web())
    # updater.update()

main()
