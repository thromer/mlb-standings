from typing import Literal, List, Union

Dimension = Literal['DIMENSION_UNSPECIFIED', 'ROWS', 'COLUMNS']
SheetValue = str | int
SheetArray = list[list[SheetValue]]
