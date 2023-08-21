# noinspection PyUnresolvedReferences
from typing import Union
from mlbstandings.typing_protocols import *
from mlbstandings.shared_types import *


class FakeDrive:
    def __init__(self) -> None:
        pass

    def get_spreadsheet_id(self, name: str) -> str:
        # return something!
        raise ValueError('implement fake getSpreadsheetId!')


class FakeSpreadsheet:
    def __init__(self, spreadsheet_id: str) -> None:
        self.id = spreadsheet_id

    def sheet(self, name: str) -> SheetLike:
        raise NotImplementedError()

    def get_named_cell(self, name: str) -> Union[str, int]:
        raise NotImplementedError()

    def set_named_cell(self, name: str, value: Union[str, int]) -> None:
        raise NotImplementedError()

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        raise NotImplementedError()

    def get_range(self, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        raise NotImplementedError()


class FakeSpreadsheets:
    def __init__(self) -> None:
        pass

    def spreadsheet(self, spreadsheet_id: str) -> SpreadsheetLike:
        return FakeSpreadsheet(spreadsheet_id)


class FakeWeb:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir

    def read(self, url: str) -> str:
        if url != 'https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml':
            raise ValueError(f'{url} unsupported by FakeWeb')
        with open(f'{self.data_dir}/{url.split("/")[-1]}') as f:
            return f.read()
