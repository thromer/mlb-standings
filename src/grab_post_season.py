#!/usr/bin/env python3
import itertools
import json

# https://statsapi.mlb.com/api/v1/schedule/postseason?season=2022
# just use checksum to see if we've processed it before
# good fields include
FIELDS = [
    'gameType', # F, D, L, W
    'gamesInSeries',
    'seriesGameNumber',
    'status.statusCode', # F if over
    'teams.away.score',
    'teams.away.team.id',
    'description[0]',  # N, A, or W
]

# Full example:
"""
{'calendarEventID': '14-715748-2022-10-11',
 'content': {'link': '/api/v1/game/715748/content'},
 'dayNight': 'night',
 'description': 'NLDS Game 1',
 'doubleHeader': 'N',
 'gameDate': '2022-10-12T01:37:00Z',
 'gameGuid': '0c5bdcc8-f9f3-4e30-95b1-c5990f06fd1d',
 'gameNumber': 1,
 'gamePk': 715748,
 'gameType': 'D',
 'gamedayType': 'P',
 'gamesInSeries': 5,
 'ifNecessary': 'N',
 'ifNecessaryDescription': 'Normal Game',
 'inningBreakLength': 120,
 'isFeaturedGame': False,
 'isTie': False,
 'link': '/api/v1.1/game/715748/feed/live',
 'officialDate': '2022-10-11',
 'publicFacing': True,
 'recordSource': 'S',
 'reverseHomeAwayStatus': False,
 'scheduledInnings': 9,
 'season': '2022',
 'seasonDisplay': '2022',
 'seriesDescription': 'Division Series',
 'seriesGameNumber': 1,
 'status': {'abstractGameCode': 'F',
            'abstractGameState': 'Final',
            'codedGameState': 'F',
            'detailedState': 'Final',
            'startTimeTBD': False,
            'statusCode': 'F'},
 'teams': {'away': {'isWinner': False,
                    'leagueRecord': {'losses': 1, 'pct': '.000', 'wins': 0},
                    'score': 3,
                    'seriesNumber': 3,
                    'splitSquad': False,
                    'team': {'id': 135,
                             'link': '/api/v1/teams/135',
                             'name': 'San Diego Padres'}},
           'home': {'isWinner': True,
                    'leagueRecord': {'losses': 0, 'pct': '1.000', 'wins': 1},
                    'score': 5,
                    'seriesNumber': 3,
                    'splitSquad': False,
                    'team': {'id': 119,
                             'link': '/api/v1/teams/119',
                             'name': 'Los Angeles Dodgers'}}},
 'tiebreaker': 'N',
 'venue': {'id': 22, 'link': '/api/v1/venues/22', 'name': 'Dodger Stadium'}}
"""

with open('/tmp/x') as f:
    j = json.load(f)

print('description,gameType,seriesGameNumber,gamesInSeries,awayId,homeId,awayScore,homeScore')
for x in itertools.chain.from_iterable([d['games'] for d in j['dates']]):
    a = x['teams']['away']
    h = x['teams']['home']
    if x['status']['statusCode'] != 'F':
        continue
    print(','.join((
        x['description'][0],
        x['gameType'],
        str(x['seriesGameNumber']),
        str(x['gamesInSeries']),
        str(a['team']['id']),
        str(h['team']['id']),
        str(a['score']),
        str(h['score'])
    )))
