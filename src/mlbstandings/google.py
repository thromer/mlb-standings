import os
import google.auth

from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.metadata.readonly']

class DefaultCreds:
  def __init__(self, scopes: List[str]) -> None:
    self.creds, _ = google.auth.default(scopes=scopes)

# TODO this is too specific to running locally and has hardcoded filenames
class LocalCreds:
  def __init__(self, scopes: List[str]) -> None:
    self.creds = None
    home_dir = os.environ['HOME']
    token_file = home_dir + '/mlb-standings.json'
    credentials_file = home_dir + '/client_secret_503586827022-4det1688u753c66bgkplrn1eseno78bq.apps.googleusercontent.com.json'
    if os.path.exists(token_file):
      self.creds = Credentials.from_authorized_user_file(token_file, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not self.creds or not self.creds.valid:
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            self.creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        if self.creds is None:
          raise ValueError('No creds even after refresh or run_local_server!')
        with open(token_file, 'w') as token:
            token.write(self.creds.to_json())

class Drive:
  def __init__(self, creds: LocalCreds) -> None:
    self.service = build('drive', 'v3', credentials=creds.creds)

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
  def __init__(self, creds: LocalCreds) -> None:
    service = build('sheets', 'v4', credentials=creds.creds)
    self.spreadsheets = service.spreadsheets()
