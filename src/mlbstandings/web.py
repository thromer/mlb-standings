import backoff
import requests

class Web:
    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_time=600,
        giveup=lambda e : isinstance(e, requests.exceptions.HTTPError) and e.response.status_code not in set([429, 500, 503]),
        max_value=60
    )
    def read(url: str, headers={}) -> str:
        print(f'Web.read({url})')
        r = requests.get(url, headers=headers, stream=True)
        if r.raw._connection and r.raw._connection.sock:
            print(f'Remote IP={r.raw._connection.sock.getpeername()[0]}')
        else:
            print("Can't determine remote IP")
        r.raise_for_status()
        if r.encoding is None:
            raise ValueError(f'Missing encoding in response to GET {url}')
        return r.content.decode(r.encoding)
