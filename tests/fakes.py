class FakeDrive:
  def __init__(self) -> None:
    pass
  def drive_stuff(self) -> None:
    pass

class FakeSheet:
  def __init__(self) -> None:
    pass
  def sheet_stuff(self) -> None:
    pass

class FakeWeb:
  def __init__(self, data_dir: str) -> None:
    self.data_dir = data_dir

  def read(self, url: str) -> str:
    if url != 'https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml':
      raise ValueError(f'{url} unsupported by FakeWeb')
    with open(f'{self.data_dir}/{url.split("/")[-1]}', 'r') as f:
      return f.read()
