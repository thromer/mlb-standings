#!/usr/bin/env python3

import google.auth
import mlbstandings.google_wrappers

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly']
drive = mlbstandings.google_wrappers.Drive(google.auth.default(scopes=scopes)[0])
ss = mlbstandings.google_wrappers.Spreadsheets(google.auth.default(scopes=scopes)[0])

s = ss.spreadsheet(drive.get_spreadsheet_id('MLB Standings 2023'))
s.set_named_cell('last_day', 30)

s.readValues('nl_uploaded', 'A:A')
