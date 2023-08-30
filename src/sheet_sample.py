#!/usr/bin/env python3

import google.auth
import mlbstandings.google_wrappers

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly']
ss = mlbstandings.google_wrappers.Spreadsheets(google.auth.default(scopes=scopes)[0])

s = ss.spreadsheet('14h3hTCvXNzUqTtbegIzSE6JwetMgvtWB6xP9gv87gZs')
s.set_named_cell('last_day', 30)

s.read_values('nl_uploaded', 'A:A')
