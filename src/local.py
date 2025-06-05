import urllib3

http = urllib3.PoolManager()
resp = http.request('GET', 'https://www.baseball-reference.com/boxes/index.fcgi?year=2025&month=05&day=21')
print(f'{resp.status=}')
