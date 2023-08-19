from typing_extensions import Protocol, Union

class SpreadsheetLike(Protocol):
  def set_named_cell(self, name: str, value: Union[str, int]) -> None: ...

class SpreadsheetsLike(Protocol):
  def spreadsheet(self, id:str) -> None: ...

class WebLike(Protocol):
  def read(self, url: str) -> str: ...

class DriveLike(Protocol):
  def getSpreadsheetId(self, name: str) -> str: ...
