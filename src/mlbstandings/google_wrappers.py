from __future__ import annotations

from typing import TYPE_CHECKING, Union, List

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from googleapiclient._apis.sheets.v4.resources import SheetsResource
    from googleapiclient._apis.drive.v3.resources import DriveResource
    from google.auth.credentials import Credentials

from googleapiclient.discovery import build


class Drive:
    def __init__(self, creds: Credentials) -> None:
        self.service: DriveResource = build('drive', 'v3', credentials=creds)

    # TODO too much hard-coding!
    def getSpreadsheetId(self, name: str) -> str:
        esc_name = name.replace("'", "\\'")
        query = (f"name='{esc_name}' and "
                 "'tromer@gmail.com' in owners and "
                 "mimeType = 'application/vnd.google-apps.spreadsheet'")
        response = self.service.files().list(q=query,
                                             spaces='drive',
                                             fields='files(id)').execute()
        files = response.get('files', [])
        if len(files) == 0:
            raise ValueError(f'{name} not found')
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

    def set_named_cell(self, name: str, value: Union[str, int]) -> None:
        vals = [[value]]
        self.spreadsheets.values().update(spreadsheetId=self.id,
                                          range=name,
                                          valueInputOption='RAW',
                                          body={'values': vals}).execute()

    def readValues(self, sheetName, range) -> List[List[Union[str, int]]]:
        result = self.spreadsheets.values().get(
            spreadsheetId=self.id,
            majorDimension="COLUMNS",
            valueRenderOption="UNFORMATTED_VALUE",
            dateTimeRenderOption="SERIAL_NUMBER",
            range=f'{sheetName}!{range}'
        ).execute().get('values', [])
        return result


class Spreadsheets:
    def __init__(self, creds: Credentials) -> None:
        service: SheetsResource = build('sheets', 'v4', credentials=creds)
        self.spreadsheets = service.spreadsheets()

    def spreadsheet(self, spreadsheet_id: str) -> Spreadsheet:
        return Spreadsheet(self.spreadsheets, spreadsheet_id)
