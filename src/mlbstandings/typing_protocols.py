from typing_extensions import Protocol, Union

class SheetLike(Protocol):
  pass

class SpreadsheetLike(Protocol):
  def sheet(self, name: str) -> SheetLike: ...
  def set_named_cell(self, name: str, value: Union[str, int]) -> None: ...

class SpreadsheetsLike(Protocol):
  def spreadsheet(self, id:str) -> SpreadsheetLike: ...

class WebLike(Protocol):
  def read(self, url: str) -> str: ...

class DriveLike(Protocol):
  def getSpreadsheetId(self, name: str) -> str: ...
