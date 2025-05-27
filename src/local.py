import urllib3

http = urllib3.PoolManager()
resp = http.request('GET', 'https://www.baseball-reference.com/')
print(f'{resp.status=}')
