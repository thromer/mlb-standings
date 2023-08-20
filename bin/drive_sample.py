#!/usr/bin/env python3

import google.auth
import mlbstandings.google_wrappers

scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.metadata.readonly']
drive = mlbstandings.google_wrappers.Drive(google.auth.default(scopes=scopes)[0])
print(drive.getSpreadsheetId('MLB Standings 2023'))
