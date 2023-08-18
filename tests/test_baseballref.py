from fakes import FakeWeb
from mlbstandings.baseballref import BaseballReference

from datetime import datetime

def testOpeningDay() -> None:
  web = FakeWeb('test-data')  # TODO is relative path really ok?
  bref = BaseballReference(web)
  assert(bref.opening_day(datetime(2023, 1, 1)) == datetime(2023, 3, 30))
  
