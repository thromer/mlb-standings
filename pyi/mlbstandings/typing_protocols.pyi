from typing_extensions import Protocol

class SheetLike(Protocol):
    def sheet_stuff(self) -> None: ...

class WebLike(Protocol):
    def read(self, url: str) -> str: ...

class DriveLike(Protocol):
    def drive_stuff(self) -> None: ...
