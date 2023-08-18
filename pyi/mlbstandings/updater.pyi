from mlbstandings.typing_protocols import *
from _typeshed import Incomplete
from datetime import datetime

class Updater:
    now: Incomplete
    drive: Incomplete
    web: Incomplete
    def __init__(self, now: datetime, drive: DriveLike, web: WebLike) -> None: ...
    def update(self) -> None: ...
