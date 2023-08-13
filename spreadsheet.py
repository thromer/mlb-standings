class Spreadsheet:

  def __init__(self, year):
    self.year = year

  def newest_entry(self, sheet_name):
    """Return (date, [data]) for the newest entry in sheet_name"""
    return (None, [])

  def upsert_entry(self, sheet_name, date, data):
    """Update or insert entry for date with with data"""
    pass

  """
  TODO maybe
  * Clear out data if it is from the wrong year?
  """

  
