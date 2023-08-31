#!/usr/bin/env python

import google.auth
import pprint
from googleapiclient.discovery import build


SHEET_ID = '14h3hTCvXNzUqTtbegIzSE6JwetMgvtWB6xP9gv87gZs'


def main():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = google.auth.default(scopes=scopes)[0]
    # https://developers.google.com/sheets/api/samples/sheet#read-sheet
    # GET https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID?&fields=sheets.properties
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/get
    # https://developers.google.com/sheets/api/guides/field-masks
    spreadsheets = build('sheets', 'v4', credentials=creds).spreadsheets()
    answer = spreadsheets.get(spreadsheetId=SHEET_ID, fields='sheets.properties(sheetId,title),sheets(charts)').execute()
    pprint.pprint(answer)


main()
