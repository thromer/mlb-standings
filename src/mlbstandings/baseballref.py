import hashlib
import json

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

MLB_ABBRS = {
 108: 'ANA',
 109: 'ARI',
 110: 'BAL',
 111: 'BOS',
 112: 'CHC',
 113: 'CIN',
 114: 'CLE',
 115: 'COL',
 116: 'DET',
 117: 'HOU',
 118: 'KC',
 119: 'LA',
 120: 'WAS',
 121: 'NYM',
 133: 'OAK',
 134: 'PIT',
 135: 'SD',
 136: 'SEA',
 137: 'SF',
 138: 'STL',
 139: 'TB',
 140: 'TEX',
 141: 'TOR',
 142: 'MIN',
 143: 'PHI',
 144: 'ATL',
 145: 'CWS',
 146: 'MIA',
 147: 'NYY',
 158: 'MIL'
}
_CANONICAL_MLB_TEAM_ABBRS = {
    'ANA': 'LAA',
    'CWS': 'CHW',
    'LA': 'LAD',
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

SCHEDULE_DATES_URL_FORMAT = (
    'https://statsapi.mlb.com/api/v1/schedule/?sportId=1&leagueId=103,104&scheduleTypes=games&gameTypes=%s&'
    'fields=dates,games,officialDate')
REGULAR_SEASON_ID = 'R'
WORLD_SERIES_ID = 'W'


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
        """First scheduled day of season. day should be during the season."""
        y = year.year
        if year != date(y, 1, 1):
            raise ValueError(f'year field should be for January 1, is {year}')
        url = '&'.join([
            SCHEDULE_DATES_URL_FORMAT % REGULAR_SEASON_ID,
            f"startDate=01/01/{y}",
            f"endDate=12/31/{y}"])
        j = json.loads(self.web.read(url))
        date_str = j['dates'][0]['games'][0]['officialDate']
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def last_scheduled_day(self, day: date, type_id: str) -> date:
        """Last scheduled day with games on or after day. day should be during the season."""
        url = '&'.join([
            SCHEDULE_DATES_URL_FORMAT % type_id,
            f"startDate={day.strftime('%m/%d/%Y')}",
            f"endDate=12/31/{day.year}"])
        j = json.loads(self.web.read(url))
        date_str = j['dates'][-1]['games'][-1]['officialDate']
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def last_scheduled_regular_day(self, day: date) -> date:
        """Last scheduled day with games on or after day. day should be during the season."""
        return self.last_scheduled_day(day, REGULAR_SEASON_ID)

    def last_scheduled_world_series_day(self, day: date) -> date:
        """Last scheduled day with games on or after day. day should be during the season."""
        return self.last_scheduled_day(day, WORLD_SERIES_ID)

    @staticmethod
    def no_games(s: bs4.BeautifulSoup) -> bool:
        for h3 in s.find(id='content').find_all('h3'):
            if h3.text == 'No Games Were or Have Yet Been Played on This Date':
                return True
        return False

    def spreadsheet_row(self, day: date) -> Optional[Dict[str, List[Union[str, int]]]]:
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
        if self.no_games(soup):
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

    @staticmethod
    def mlb_id_to_abbr(id: int) -> str:
        mlb_abbr = MLB_ABBRS[id]
        if mlb_abbr in _CANONICAL_MLB_TEAM_ABBRS:
            return _CANONICAL_MLB_TEAM_ABBRS[mlb_abbr]
        return mlb_abbr

    def grab_post_season(self, year: date):
        url = (f'https://statsapi.mlb.com/api/v1/schedule/postseason?season={year.year}&'
               'fields=copyright,dates,date,games,status,statusCode,description,gameType,'
               'seriesGameNumber,gamesInSeries,teams,team,id,score')
        d = self.web.read(url)
        md5 = hashlib.md5(d.encode('UTF-8')).hexdigest()
        j = json.loads(d)
        header = ['description', 'gameType', 'seriesGameNumber', 'gamesInSeries',
                  'awayId', 'homeId', 'awayScore', 'homeScore']
        rows = []
        for x in itertools.chain.from_iterable([d['games'] for d in j['dates']]):
            a = x['teams']['away']
            h = x['teams']['home']
            if x['status']['statusCode'] != 'F':
                continue
            rows.append([
                x['description'][0],
                x['gameType'],
                x['seriesGameNumber'],
                x['gamesInSeries'],
                self.mlb_id_to_abbr(a['team']['id']),
                self.mlb_id_to_abbr(h['team']['id']),
                a['score'],
                h['score']])
        return {
            'md5': md5, 'header': header, 'rows': rows,
            'last_scheduled_day': datetime.strptime(max([d['date'] for d in j['dates']]), '%Y-%m-%d').date()}
