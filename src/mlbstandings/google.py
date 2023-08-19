from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
  from googleapiclient._apis.sheets.v4.resources import SheetsResource
  from googleapiclient._apis.drive.v3.resources import DriveResource

import os
import google.auth

from typing import List

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
    response = self.service.files().list(q=f"name='{esc_name}'",
                                    spaces='drive',
                                    fields='files(id)').execute()
    files = response.get('files', [])
    if len(files) == 0:
      raise ValueError(f'{name} not found')
    elif len(files) > 1:
      raise ValueError(f'{len(files)} files named {name}')
    id = files[0].get('id')
    if not isinstance(id, str):
      raise ValueError(f'{id} is not a string?!')
    return id

class Spreadsheet:
  def __init__(self, spreadsheets: SheetsResource.SpreadsheetsResource, id: str) -> None:
    self.spreadsheets = spreadsheets
    self.id = id

  def set_named_cell(self, name: str, value: Union[str, int]) -> None:
    vals = [[value]]
    self.spreadsheets.values().update(spreadsheetId=self.id,
                                      range=name,
                                      valueInputOption='RAW',
                                      body={'values':vals}).execute()

class Spreadsheets:
  def __init__(self, creds: Credentials) -> None:
    service: SheetsResource = build('sheets', 'v4', credentials=creds)
    self.spreadsheets = service.spreadsheets()

  def spreadsheet(self, id: str) -> Spreadsheet:
    return Spreadsheet(self.spreadsheets, id)
