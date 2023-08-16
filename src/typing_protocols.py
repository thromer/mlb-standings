from typing_extensions import Protocol

class SheetLike(Protocol):
  def sheet_stuff(self) -> None: ...

class WebLike(Protocol):
  def web_stuff(self) -> None: ...

class DriveLike(Protocol):
  def drive_stuff(self) -> None: ...
  
