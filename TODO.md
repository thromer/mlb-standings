Probably not: switch to statsapi for regular season. Unfortunately it doesn't take care of tiebreakers correctly, e.g. looking at 8/29/2023 it put the Mariners ahead of the Rangers even though they had idential records and Texas was 5-1 head-to-head. This is a good reference in general for statsapi: https://controlc.com/b71582de in general for statsapi

baseball-reference got it right on 8/29, though you never can tell whether that's because they were lucky or actually computed the tiebreaker correctly.

e.g.

https://statsapi.mlb.com/api/v1/standings?sportId=1&leagueId=103,104&season=2023&date=08/29/2023&fields=copyright,records,teamRecords,team,id,name,divisionRank,wildCardRank,leagueRecord,wins,losses

Exception / error handling

Maybe put in Cloud Firestore or similar instead of sheets, and have sheets pull from that. Consider https://github.com/toddrob99/MLB-StatsAPI/wiki

Future: Graph post-season automatically. Suggest not trying too hard to generalize across the different incarnations of wildcard formats. BR has the scores. Has brackets for past seasons but when are they populated? (See: https://www.baseball-reference.com/leagues/majors/2022.shtml and series linked from there.)

Tiebreakers.

Dynamically computed jitter in numbers so that tied teams are distinct in graphs.

