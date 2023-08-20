from typing import List, Tuple


class Spreadsheet:

    def __init__(self, year: int) -> None:
        self.year = year

    def newest_entry(self, sheet_name: str) -> Tuple[int, List[str]]:
        """Return (date, [data]) for the newest entry in sheet_name"""
        return (1234, [])

    # def upsert_entry(self, sheet_name, date, data) -> None:
    #   """Update or insert entry for date with with data"""
    #   pass

    """
  TODO maybe
  * Clear out data if it is from the wrong year?
  """
