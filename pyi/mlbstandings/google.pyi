from _typeshed import Incomplete
from google.oauth2.credentials import Credentials

class LocalCreds:
    creds: Incomplete
    def __init__(self, scopes) -> None: ...

class Drive:
    def __init__(self, creds: Credentials) -> None: ...

class Spreadsheets:
    spreadsheets: Incomplete
    def __init__(self, creds: Credentials) -> None: ...
