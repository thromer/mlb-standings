import urllib.error

# TODO remove once we're running on a system that works with urllib3 + baseball-reference.com
import urllib.request  # import Request, urlopen

import backoff
import requests


class Web:
    @staticmethod
    def retryable(code: int) -> bool:
        return False  # TODO
    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.HTTPError, urllib.error.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_time=600,
        giveup=lambda e : isinstance(e, requests.exceptions.HTTPError) and e.response.status_code not in set([429, 500, 503]),
        max_value=60
    )
    def read(url: str) -> str:
        print(f'Web.read({url}')
        if url.find('https://www.baseball-reference.com/') == 0:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req) 
            return resp.read().decode('ISO-8859-1')
        r = requests.get(url)
        r.raise_for_status()
        if r.encoding is None:
            raise ValueError(f'Missing encoding in esponse to GET {url}')
        return r.content.decode(r.encoding)
