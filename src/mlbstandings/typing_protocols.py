from typing import Any, Protocol

from mlbstandings.shared_types import Dimension, SheetArray, SheetValue


class SheetLike(Protocol):
    pass


class SpreadsheetLike(Protocol):
    def set_range(self, range_str: str, values: SheetArray) -> None: ...

    def set_cell(self, cell_str: str, value: SheetValue) -> None: ...

    def get_range(
        self, range_str: str, major_dimension: Dimension = "ROWS"
    ) -> SheetArray: ...

    def get_cell(self, cell_str: str) -> SheetValue: ...

    def append_to_range(self, range_str: str, values: SheetArray) -> dict[str, Any]: ...

    def clear_range(self, range_str: str) -> None: ...

    def clear_sheet(self, sheet_name: str) -> None: ...


class SpreadsheetsLike(Protocol):
    def spreadsheet(self, spreadsheet_id: str) -> SpreadsheetLike: ...


class FilesLike(Protocol):
    def copy(self, id: str, name: str) -> str: ...


class RateLimiterLike(Protocol):
    def delay(self) -> None: ...


class WebLike(Protocol):
    def read(self, url: str) -> str: ...


class StatsLike(Protocol): ...
