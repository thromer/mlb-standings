from typing_protocols import *

from bs4 import BeautifulSoup
from datetime import datetime

class BaseballReference:
  def __init__(self, web: WebLike) -> None:
    self.web = web

  # TODO keep this in a persistent cache like python-cachier, diskcache, shelve ... though not for tests.
  def opening_day(self, year: datetime) -> datetime:
    if year != datetime(year.year, 1, 1):
      raise ValueError(f'year field should be for January 1, is {year}')
    url = f'https://www.baseball-reference.com/leagues/majors/{year.year}-schedule.shtml'
    data = self.web.read(url)
    soup = BeautifulSoup(data, features='html.parser')
    h3 = soup.find('h3')
    if h3 is None:
      raise ValueError(f'h3 element not found in {url}')
    day_text = h3.text  # 'Thursday, March 30, 2023'
    return datetime.strptime(day_text, '%A, %B %d, %Y')

