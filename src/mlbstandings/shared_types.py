from typing import Literal, List, Union

Dimension = Literal['DIMENSION_UNSPECIFIED', 'ROWS', 'COLUMNS']
SheetArray = List[List[Union[str, int]]]
