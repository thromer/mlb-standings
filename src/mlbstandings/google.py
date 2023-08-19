import os
import google.auth

from typing import List

from google.auth.credentials import Credentials
from googleapiclient.discovery import build

class Drive:
  def __init__(self, creds: Credentials) -> None:
    self.service = build('drive', 'v3', credentials=creds)

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

class Spreadsheets:
  def __init__(self, creds: Credentials) -> None:
    service = build('sheets', 'v4', credentials=creds)
    self.spreadsheets = service.spreadsheets()
