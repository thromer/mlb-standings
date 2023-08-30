import bs4
import itertools

from mlbstandings.typing_protocols import *
from datetime import date, datetime
from functools import cache

from typing import List, Dict, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mlbstandings.shared_types import SheetValue


_CANONICAL_TEAM_ABBRS = {
    'TBR': 'TB',
    'KCR': 'KC',
    'SDP': 'SD',
    'SFG': 'SF',
    'WSN': 'WAS'
}

_CANONICAL_DIVISION_NAMES = {
    'E': 'East',
    'C': 'Central',
    'W': 'West'
}

# A bit of a cheat: league and division names are implicitly the same as used in baseball reference.
LEAGUES = {
    'AL': {
        'E': ['BAL', 'BOS', 'NYY', 'TB', 'TOR'],
        'C': ['CHW', 'CLE', 'DET', 'KC', 'MIN'],
        'W': ['HOU', 'LAA', 'OAK', 'SEA', 'TEX']
    },
    'NL': {
        'E': ['ATL', 'MIA', 'NYM', 'PHI', 'WAS'],
        'C': ['CHC', 'CIN', 'MIL', 'PIT', 'STL'],
        'W': ['ARI', 'COL', 'LAD', 'SD', 'SF'],
    }
}

LEAGUE_TEAMS = {
    league: list(itertools.chain.from_iterable(LEAGUES[league].values()))
    for league in LEAGUES.keys()
}

DIVISION_ORDER = ['E', 'C', 'W']


class Standings:
    def __init__(self, league: str, stats: Dict[str, Dict[str, float]]):
        self.league = league
        self.stats = stats
        self.divisions = LEAGUES[league]
        self.all_teams = LEAGUE_TEAMS[league]
        # Get sole leader(s) for each division, so we can exclude them from WC list
        sole_leaders = set()
        for div_teams in self.divisions.values():
            count_best = 0
            best = float('-inf')
            sole = None
            for t in div_teams:
                pct = self.stats[t]['pct']
                if pct == best:
                    count_best += 1
                    sole = None
                elif pct > best:
                    best = pct
                    count_best = 1
                    sole = t
            if sole is not None:
                sole_leaders.add(sole)

        # +/- .500
        # plus_minus: List[Union[str, int]] = [int(stats[t]['w'] - stats[t]['l']) for t in all_teams]

        self.div_orders: Dict[str, List[str]] = {
            # sort by negative winning pct, then by abbr (both ascending)
            # TODO probably should make sort step a function since it is repeated below.
            division: sorted(sorted(self.divisions[division]), key=lambda team: -stats[team]['pct'])
            for division in self.divisions.keys()
        }

        wc_teams = set(self.all_teams) - sole_leaders
        self.wc_order: List[str] = sorted(sorted(wc_teams), key=lambda team: -stats[team]['pct'])

    def plus_minus(self) -> Dict[str, int]:
        return {t: int(self.stats[t]['w'] - self.stats[t]['l']) for t in self.all_teams}

    def row(self) -> List[Union[str, int]]:
        pm = self.plus_minus()
        div_orders: List[str] = list(itertools.chain.from_iterable([self.div_orders[d] for d in DIVISION_ORDER]))
        plus_minus: List[int] = [pm[t] for t in self.all_teams]
        result = plus_minus + div_orders + self.wc_order
        return result


class BaseballReference:
    def __init__(self, web: WebLike) -> None:
        self.web = web

    @staticmethod
    @cache
    def canonicalize_abbr(abbr: str) -> str:
        if abbr in _CANONICAL_TEAM_ABBRS:
            return _CANONICAL_TEAM_ABBRS[abbr]
        return abbr

    def first_day(self, year: date) -> date:
        if year != date(year.year, 1, 1):
            raise ValueError(f'year field should be for January 1, is {year}')
        url = f'https://www.baseball-reference.com/leagues/majors/{year.year}-schedule.shtml'
        data = self.web.read(url)
        soup = bs4.BeautifulSoup(data, features='html.parser')
        h3 = soup.find('h3')
        if h3 is None:
            raise ValueError(f'h3 element not found in {url}')
        day_text = h3.text  # 'Thursday, March 30, 2023'
        return date.fromtimestamp(datetime.strptime(day_text, '%A, %B %d, %Y').timestamp())

    def something(self, day: date) -> Optional[Dict[str, List[Union[str, int]]]]:
        """Returns ready-to-paste rows (other than day) for the day if available, None otherwise"""
        url = day.strftime('https://www.baseball-reference.com/boxes/?year=%Y&month=%m&day=%d')
        data = self.web.read(url)
        soup = bs4.BeautifulSoup(data, features='html.parser')
        today_button = soup.find('span', class_='button2 current')
        if today_button is None or type(today_button) is not bs4.element.Tag:
            raise ValueError(f'Unable to find current date in {url}')
        br_day_text = today_button.text
        br_day = datetime.strptime(br_day_text, '%b %d, %Y').date()
        if br_day != day:
            return None
        return {
            league: self._work(league, soup).row() for league in LEAGUES
        }

    def _work(self, league: str, soup: bs4.BeautifulSoup) -> Standings:
        table_id = f'standings-upto-{league}-overall'
        overall_table = soup.find(id=table_id)
        if overall_table is not None and type(overall_table) == bs4.element.Tag:
            overall_table = overall_table.tbody
        if overall_table is None or type(overall_table) != bs4.element.Tag:
            raise ValueError(f'{table_id} is missing or exists with no tbody')

        # Get everyone's stats
        stats = {}
        for tr in overall_table.find_all('tr'):
            tds = tr.find_all('td')
            abbr = self.canonicalize_abbr(tr.th.text)
            wins = int(tds[0].text)
            losses = int(tds[1].text)
            stats[abbr] = {'w': wins, 'l': losses, 'pct': 0.5 if wins + losses == 0 else wins / (wins + losses)}

        return Standings(league, stats)

    @staticmethod
    def zeroday() -> Optional[Dict[str, List[Union[str, int]]]]:
        stats = {abbr: {'w': 0, 'l': 0, 'pct': 0.5} for abbr in itertools.chain.from_iterable(LEAGUE_TEAMS.values())}
        return {league: Standings(league, stats).row() for league in LEAGUES.keys()}

    @staticmethod
    def header_row(league: str) -> List[SheetValue]:
        divs = LEAGUES[league]
        return list(
            itertools.chain.from_iterable(
                [list(itertools.chain.from_iterable(divs.values()))] +
                [[f'{league} {x}'] + ['']*4 for x in [_CANONICAL_DIVISION_NAMES[div] for div in divs.keys()]] +
                [['Wildcard']]))
