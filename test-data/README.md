https://www.baseball-reference.com/teams/BOS/2023-schedule-scores.shtml  for each team beginning of the day 2023-08-12.


for t in $(grep  "^      '" ../constants.py| perl -p -e "s@'|,@@g") ; do curl "https://www.baseball-reference.com/teams/${t}/2023-schedule-scores.shtml" > ${t}.shtml; done
wget https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml
curl 'https://www.baseball-reference.com/boxes/?year=2023&month=3&day=31'  > boxes-2023-03-31.html
curl 'https://www.baseball-reference.com/boxes/?year=2023&month=3&day=30'  > boxes-2023-03-30.html
for d in $(seq 1 30) ; do sleep 10; curl "https://www.baseball-reference.com/boxes/?year=2023&month=4&day=${d}"  > boxes-2023-04-${d}.html ; done
for f in boxes-2023-04-?.html ; do mv -i $f $(echo $f | perl -p -e 's@2023-04-@2023-04-0@') ; done

