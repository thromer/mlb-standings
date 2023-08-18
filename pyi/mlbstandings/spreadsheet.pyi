from _typeshed import Incomplete
from typing import List, Tuple

class Spreadsheet:
    year: Incomplete
    def __init__(self, year: int) -> None: ...
    def newest_entry(self, sheet_name: str) -> Tuple[int, List[str]]: ...
