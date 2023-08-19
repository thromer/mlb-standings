from typing import Union

class FakeDrive:
  def __init__(self) -> None:
    pass
  def getSpreadsheetId(self, name: str) -> str:
    # return something!
    raise ValueError('implement fake getSpreadsheetId!')

class FakeSpreadsheet:
  def __init__(self, id: str) -> None:
    self.id = id
  def set_named_cell(self, name: str, value: Union[str, int]) -> None:
    raise ValueError('implement FakeSpreadsheet.set_named_cell')

class FakeSpreadsheets:
  def __init__(self) -> None:
    pass
  def spreadsheet(self, id:str) -> FakeSpreadsheet:
    return FakeSpreadsheet(id)

class FakeWeb:
  def __init__(self, data_dir: str) -> None:
    self.data_dir = data_dir

  def read(self, url: str) -> str:
    if url != 'https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml':
      raise ValueError(f'{url} unsupported by FakeWeb')
    with open(f'{self.data_dir}/{url.split("/")[-1]}', 'r') as f:
      return f.read()
