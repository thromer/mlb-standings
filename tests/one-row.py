#!/usr/bin/env python3

import bs4
import sys

from functools import cache
from functools import reduce

CANONICAL_ABBRS = {
  'TBR': 'TB',
  'KCR': 'KC',
  # TODO add national league versions
}

DIVISIONS = ['E', 'C', 'W']  # Cheat: abbreviations in BR html.
TEAMS = {
  'E': ['BAL', 'BOS', 'NYY', 'TB', 'TOR'],
  'C': ['CHW', 'CLE', 'DET', 'KC', 'MIN'],
  'W': ['HOU', 'LAA', 'OAK', 'SEA', 'TEX']
}

@cache
def canonicalize_abbr(abbr):
  if abbr in CANONICAL_ABBRS:
    return CANONICAL_ABBRS[abbr]
  return abbr

def division(soup, league, division):
  # we want to know:
  #   each team's win loss record
  #   list of teams in first (not the prettiest place to do it)
  pass



def work(league, data):
  soup = bs4.BeautifulSoup(data, features='html.parser')
  overall_table = soup.find(id=f'standings-upto-{league}-overall').tbody

  # Get everyone's stats
  stats = {}
  for tr in overall_table.find_all('tr'):
    tds = tr.find_all('td')
    abbr = canonicalize_abbr(tr.th.text)
    w = int(tds[0].text)
    l = int(tds[1].text)
    stats[abbr] = { 'w': w, 'l': l, 'pct': 0.5 if w + l == 0 else w / (w + l) }

  # Get sole leader(s) for each division, so we can exclude them from WC list
  sole_leaders = set()
  for div_teams in TEAMS.values():
    count_best = 0
    best = float('-inf')
    for t in div_teams:
      pct = stats[t]['pct']
      if pct == best:
        count_best += 1
        sole = None
      elif pct > best:
        best = pct
        count_best = 1
        sole = t
    if sole:
      sole_leaders.add(sole)

  all_teams = reduce(list.__add__, TEAMS.values())

  # +/- .500
  plus_minus = [stats[t]['w'] - stats[t]['l'] for t in all_teams]

  # TODO NOW left out division order!!!
  div_orders = [
    # probably should make this is a function since it is repeated below.
    sorted(sorted(div_teams), key=lambda t: -stats[t]['pct'])
    for div_teams in TEAMS.values()
  ]
  div_order = reduce(list.__add__, div_orders)

  # For WC list, sort by negative winning pct, then by abbr (both ascending)
  wc_teams = set(all_teams) - sole_leaders
  wc_order = sorted(sorted(wc_teams), key=lambda t: -stats[t]['pct'])

  return plus_minus + div_order + wc_order
  
def main():
  data = sys.stdin.read()
  full_result = ['2023-04-30'] + work('AL', data)
  print(','.join([str(x) for x in full_result]))

main()
