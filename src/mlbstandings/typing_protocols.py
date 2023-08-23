from typing import Union, Protocol

from mlbstandings.shared_types import Dimension, SheetArray


class SheetLike(Protocol):
    pass


class SpreadsheetLike(Protocol):
    # def sheet(self, name: str) -> SheetLike: ...

    def get_named_cell(self, name: str) -> Union[str, int]: ...

    def set_named_cell(self, name: str, value: Union[str, int]) -> None: ...

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray: ...

    def write_values(self, sheet_name: str, sheet_range: str, values: SheetArray, major_dimension: Dimension = 'ROWS') -> None: ...


class SpreadsheetsLike(Protocol):
    def spreadsheet(self, spreadsheet_id: str) -> SpreadsheetLike: ...


class WebLike(Protocol):
    def read(self, url: str) -> str: ...


class DriveLike(Protocol):
    def get_spreadsheet_id(self, name: str) -> str: ...
