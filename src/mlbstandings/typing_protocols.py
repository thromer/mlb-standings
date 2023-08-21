from typing import Union
from typing_extensions import Protocol


class SheetLike(Protocol):
    pass


class SpreadsheetLike(Protocol):
    def sheet(self, name: str) -> SheetLike: ...

    def get_named_cell(self, name: str) -> Union[str, int]: ...

    def set_named_cell(self, name: str, value: Union[str, int]) -> None: ...


class SpreadsheetsLike(Protocol):
    def spreadsheet(self, spreadsheet_id: str) -> SpreadsheetLike: ...


class WebLike(Protocol):
    def read(self, url: str) -> str: ...


class DriveLike(Protocol):
    def get_spreadsheet_id(self, name: str) -> str: ...
