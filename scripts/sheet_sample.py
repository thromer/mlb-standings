#!/usr/bin/env python3

import google.auth
from google.auth.transport.requests import AuthorizedSession

import mlbstandings.light_google_wrappers

# More scopes? Re-run gcloud auth application-default login
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly']
ss = mlbstandings.light_google_wrappers.Spreadsheets(AuthorizedSession(google.auth.default(scopes=scopes)[0]))  # type: ignore

s = ss.spreadsheet('1ci-zPNJ8s0ZHbm9OBG49dF_DIOGloQPQKF3rmNUwZvA')
print(s.get_range('Sheet1!A:A'))
s.set_range('Sheet1!A1:A2', [[7],[8]])
res=s.append_to_range('Sheet1!A1:C', [[9],[10]])
print(f'append returned {res}')
print(s.get_range('Sheet1!A:A'))
s.clear_sheet('Sheet1')


      
