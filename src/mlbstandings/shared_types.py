from typing import Literal, List, Union

Dimension = Literal['DIMENSION_UNSPECIFIED', 'ROWS', 'COLUMNS']
SheetValue = Union[str, int]
SheetArray = List[List[SheetValue]]
