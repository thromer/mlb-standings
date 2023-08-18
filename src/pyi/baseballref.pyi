from typing_protocols import *
from _typeshed import Incomplete
from datetime import datetime

class BaseballReference:
    web: Incomplete
    def __init__(self, web: WebLike) -> None: ...
    def opening_day(self, year: datetime) -> datetime: ...
