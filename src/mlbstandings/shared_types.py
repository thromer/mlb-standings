from typing import Literal


Dimension = Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"]
SheetValue = str | int
SheetArray = list[list[SheetValue]]
