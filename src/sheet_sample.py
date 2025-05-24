#!/usr/bin/env python3

import google.auth

from google.auth.transport.requests import AuthorizedSession

import mlbstandings.light_google_wrappers

# More scopes? Re-run gcloud auth application-default login
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly']
ss = mlbstandings.light_google_wrappers.Spreadsheets(AuthorizedSession(google.auth.default(scopes=scopes)[0]))  # type: ignore

s = ss.spreadsheet('14h3hTCvXNzUqTtbegIzSE6JwetMgvtWB6xP9gv87gZs')
s.set_cell('last_day', 30)

s.get_range('nl_uploaded!A:A')
