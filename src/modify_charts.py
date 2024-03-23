#!/usr/bin/env python

import google.auth
import pprint
from googleapiclient.discovery import build

SHEET_ID = '14h3hTCvXNzUqTtbegIzSE6JwetMgvtWB6xP9gv87gZs'
SHEET_TITLE = 'hacked copy of all'
CHART_ID = 411882614  # AL Central


def main():
    # More scopes? Re-run gcloud auth application-default login
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = google.auth.default(scopes=scopes)[0]
    spreadsheets = build('sheets', 'v4', credentials=creds).spreadsheets()
    sheets = spreadsheets.get(
        spreadsheetId=SHEET_ID,
        fields='sheets.properties(sheetId,title),sheets(charts)').execute()
    sheet = None
    for s in sheets['sheets']:
        if s['properties']['title'] == SHEET_TITLE:
            sheet = s
            break

    for chart in sheet['charts']:
        chart['spec']['title'] = str(chart['chartId'])
        # del chart['spec']['title']
        pass
    requests = [{
        'updateChartSpec': {
            'spec': chart['spec'],
            'chartId': chart['chartId'],
        }}
        for chart in sheet['charts']
        if chart['chartId'] == CHART_ID
    ]
    print('BEFORE')
    pprint.pprint(requests[0]['updateChartSpec']['spec'])
    requests[0]['updateChartSpec']['spec']['basicChart']['series'] = [{
        'dataLabel': {'textFormat': {'fontFamily': 'Roboto'},
                      'type': 'NONE'},
        'series': {'sourceRange': {'sources': [{'endColumnIndex': c + 1,
                                                'endRowIndex': 258,
                                                'sheetId': 1013424554,
                                                'startColumnIndex': c,
                                                'startRowIndex': 1}]}},
        'targetAxis': 'LEFT_AXIS'
    } for c in range(6, 11)
    ]
    print('AFTER')
    pprint.pprint(requests[0]['updateChartSpec']['spec'])
    # spreadsheets.batchUpdate(spreadsheetId=SHEET_ID, body={'requests': requests}).execute()


main()
