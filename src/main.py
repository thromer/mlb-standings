from typing import Optional, cast

import google.auth
import mlbstandings.google_wrappers
import flask
import functions_framework


@functions_framework.http
def cf_test(request: Optional[flask.Request]) -> str:
    print(type(request))
    if isinstance(request, flask.Request):
        request_json = request.get_json(silent=True)
        request_args = request.args
        print(f'{request_json=}')
        print(f'{request_args=}')
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = google.auth.default(scopes=scopes)[0]
    sheets = mlbstandings.google_wrappers.Spreadsheets(creds)
    spreadsheet = sheets.spreadsheet('1aPybqeHZ1o1v0Z1z2v8Ieg6CT_O6BwknIXBOndH22oo')
    before = spreadsheet.read_values('Sheet1', 'A6:A6')
    old_val = before[0][0]
    new_val = 0 if type(old_val) is str else cast(int, old_val) + 1
    print(f"Before {before}")
    spreadsheet.write_values('Sheet1', 'A6:A6', [[new_val]])
    print(f"After {spreadsheet.read_values('Sheet1', 'A6:A6')}")

    return str(new_val)
