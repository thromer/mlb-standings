from __future__ import annotations

from mlbstandings.shared_types import Dimension, SheetArray, SheetValue
from googleapiclient.discovery import build

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from googleapiclient._apis.sheets.v4.resources import SheetsResource
    # noinspection PyProtectedMember
    from googleapiclient._apis.drive.v3.resources import DriveResource
    from google.auth.credentials import Credentials


class Drive:
    def __init__(self, creds: Credentials) -> None:
        self.service: DriveResource = build('drive', 'v3', credentials=creds)

    # TODO too much hard-coding!
    def get_spreadsheet_id(self, name: str) -> str:
        esc_name = name.replace("'", "\\'")
        query = (f"name='{esc_name}' and "
                 "'tromer@gmail.com' in owners and "
                 "mimeType = 'application/vnd.google-apps.spreadsheet'")
        response = self.service.files().list(q=query,
                                             spaces='drive',
                                             fields='files(id)').execute()
        files = response.get('files', [])
        if len(files) == 0:
            raise FileNotFoundError(f'{name} not found')
        elif len(files) > 1:
            raise ValueError(f'{len(files)} files named {name}')
        file_id = files[0].get('id')
        if not isinstance(file_id, str):
            raise ValueError(f'{file_id} is not a string?!')
        return file_id


class Sheet:
    def __init__(self, spreadsheet: Spreadsheet, name: str):
        self.spreadsheets = spreadsheet.spreadsheets
        self.id = spreadsheet.id
        self.name = name


#    def read(self, r: str) -> List[List[Union[str, int]]]:
#        something = self.spreadsheets.values().get(
#          self.id,
#        ).execute().get()
#       return []


class Spreadsheet:
    def __init__(self, spreadsheets: SheetsResource.SpreadsheetsResource, spreadsheet_id: str) -> None:
        self.spreadsheets = spreadsheets
        self.id = spreadsheet_id

    def sheet(self, name: str) -> Sheet:
        return Sheet(self, name)

    def get_named_cell(self, name: str) -> SheetValue:
        range_values = self.get_range(name)
        if len(range_values) == 0:
            return ''
        return range_values[0][0]

    def set_named_cell(self, name: str, value: SheetValue) -> None:
        vals = [[value]]
        self.spreadsheets.values().update(spreadsheetId=self.id,
                                          range=name,
                                          valueInputOption='RAW',
                                          body={'values': vals}).execute()

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
