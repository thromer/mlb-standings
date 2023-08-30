from typing import Protocol

from mlbstandings.shared_types import Dimension, SheetArray, SheetValue


class SheetLike(Protocol):
    pass


class SpreadsheetLike(Protocol):
    # def sheet(self, name: str) -> SheetLike: ...
    def get_named_range(self, name: str) -> SheetArray: ...

    def get_named_cell(self, name: str) -> SheetValue: ...

    def set_named_cell(self, name: str, value: SheetValue) -> None: ...

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray: ...

    def write_values(self, sheet_name: str, sheet_range: str,
                     values: SheetArray, major_dimension: Dimension = 'ROWS') -> None: ...


class SpreadsheetsLike(Protocol):
    def spreadsheet(self, spreadsheet_id: str) -> SpreadsheetLike: ...


class RateLimiterLike(Protocol):
    def delay(self) -> None: ...


class WebLike(Protocol):
    def read(self, url: str) -> str: ...
