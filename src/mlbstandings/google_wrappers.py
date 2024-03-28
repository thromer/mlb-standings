from __future__ import annotations

from mlbstandings.shared_types import Dimension, SheetArray, SheetValue
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import backoff

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from googleapiclient._apis.drive.v3.resources import DriveResource
    from googleapiclient._apis.sheets.v4.resources import SheetsResource
    from google.auth.credentials import Credentials


def backoff_on_retryable():
    return backoff.on_exception(
        backoff.expo,
        (HttpError, TimeoutError),
        max_time=600,
        giveup=lambda e : isinstance(e, HttpError) and e.status_code not in set([429, 500, 503]),
        max_value=60
    )


class Sheet:
    def __init__(self, spreadsheet: Spreadsheet, name: str):
        self.spreadsheets = spreadsheet.spreadsheets
        self.id = spreadsheet.id
        self.name = name


class Spreadsheet:
    def __init__(self, spreadsheets: SheetsResource.SpreadsheetsResource, spreadsheet_id: str) -> None:
        self.spreadsheets = spreadsheets
        self.id = spreadsheet_id

    def sheet(self, name: str) -> Sheet:
        return Sheet(self, name)

    def get_named_range(self, name: str) -> SheetArray:
        return self.get_range(name)

    @backoff_on_retryable()
    def set_named_range(self, name: str, vals: SheetArray) -> None:
        self.spreadsheets.values().update(spreadsheetId=self.id,
                                          range=name,
                                          valueInputOption='RAW',
                                          body={'values': vals}).execute()

    def get_named_cell(self, name: str) -> SheetValue:
        range_values = self.get_named_range(name)
        if len(range_values) == 0 or len(range_values[0]) == 0:
            return ''
        return range_values[0][0]

    def set_named_cell(self, name: str, value: SheetValue) -> None:
        self.set_named_range(name, [[value]])

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        return self.get_range(f'{sheet_name}!{sheet_range}', major_dimension)

    @backoff_on_retryable()
    def get_range(self, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        response = self.spreadsheets.values().get(
            spreadsheetId=self.id,
            range=f'{sheet_range}',
            dateTimeRenderOption="SERIAL_NUMBER",
            majorDimension=major_dimension,
            valueRenderOption="UNFORMATTED_VALUE"
        ).execute()
        result = response.get('values', [[]])
        return result

    def write_values(self, sheet_name: str, sheet_range: str, values: SheetArray, major_dimension: Dimension = 'ROWS') -> None:
        self.update_range(f'{sheet_name}!{sheet_range}', values, major_dimension)

    @backoff_on_retryable()
    def update_range(self, sheet_range: str, values: SheetArray, major_dimension: Dimension = 'ROWS') -> None:
        self.spreadsheets.values().update(
            spreadsheetId=self.id,
            range=f'{sheet_range}',
            body={
                'values': values,
                'majorDimension': major_dimension,
            },
            includeValuesInResponse=False,
            valueInputOption="RAW"
        ).execute()

    @backoff_on_retryable()
    def append_to_range(self, range, rows):
        return self.spreadsheets.values().append(
            spreadsheetId=self.id,
            range=range,
            body={'majorDimension':'ROWS','values':rows},
            valueInputOption='USER_ENTERED'
        ).execute()

    @backoff_on_retryable()
    def clear_range(self, range):
        return self.spreadsheets.values().clear(
            spreadsheetId=self.id,
            range=range
        ).execute()

    def clear_sheet(self, sheet_name):
        append_res = self.append_to_range(f"'{sheet_name}'!A1:A", [['']])
        clear_range = append_res['updates']['updatedRange'].replace('!A','!1:',1)
        self.clear_range(clear_range)


class Spreadsheets:
    def __init__(self, creds: Credentials) -> None:
        service: SheetsResource = build('sheets', 'v4', credentials=creds)
        self.spreadsheets = service.spreadsheets()

    def spreadsheet(self, spreadsheet_id: str) -> Spreadsheet:
        return Spreadsheet(self.spreadsheets, spreadsheet_id)


class Files:
    def __init__(self, creds: Credentials) -> None:
        service: DriveResource = build('drive', 'v3', credentials=creds)
        self.files = service.files()

    @backoff_on_retryable()
    def copy(self, id, name):
        return self.files.copy(fileId=id, body={'name': name}).execute()['id']
