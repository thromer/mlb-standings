from __future__ import annotations

from mlbstandings.shared_types import Dimension, SheetArray, SheetValue
from googleapiclient.discovery import build

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from googleapiclient._apis.sheets.v4.resources import SheetsResource
    from google.auth.credentials import Credentials


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


class Spreadsheets:
    def __init__(self, creds: Credentials) -> None:
        service: SheetsResource = build('sheets', 'v4', credentials=creds)
        self.spreadsheets = service.spreadsheets()

    def spreadsheet(self, spreadsheet_id: str) -> Spreadsheet:
        return Spreadsheet(self.spreadsheets, spreadsheet_id)
