#!/usr/bin/env python3

import google.auth
import mlbstandings.google

scopes = ['https://www.googleapis.com/auth/spreadsheets', 
          'https://www.googleapis.com/auth/drive.metadata.readonly']
drive = mlbstandings.google.Drive(google.auth.default(scopes=scopes)[0])
ss = mlbstandings.google.Spreadsheets(google.auth.default(scopes=scopes)[0])

s = ss.spreadsheet(drive.getSpreadsheetId('MLB Standings 2023'))
s.set_named_cell('last_day', 30)

