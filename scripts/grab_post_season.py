#!/usr/bin/env python3
import itertools
import json
import sys

from datetime import date
from mlbstandings import web
from mlbstandings import baseballref
from pprint import pprint

w = web.Web()
br = baseballref.BaseballReference(w)
post_season = br.grab_post_season(date(2022, 1, 1))
print(f"last={post_season['last_scheduled_day']}")
print(f"md5={post_season['md5']}")
print(",".join(post_season['header']))
for r in post_season['rows']:
    print(",".join([str(x) for x in r]))
