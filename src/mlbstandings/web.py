import backoff
import requests
import urllib.error
import urllib.request

class Web:
    @staticmethod
    def retryable(e):
        code = None
        if isinstance(e, requests.exceptions.HTTPError):
            code = e.response.status_code
        elif isinstance(e, urllib.error):
            code = e.getcode()
        if code is None:
            return True
        return code in set([429, 500, 503])        
    
    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_time=600,
        giveup=lambda e: not retryable(e),
        max_value=60
    )
    def read(url: str) -> str:
        print(f'Web.read({url}')
        content = None
        # TODO remove use of urllib if requests+urllib3 and baseball-reference.com ever play nice
        if url.find('baseball-reference.com') > 0:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as f:
                content = f.read()
                encoding = 'ISO-8859-1'  # yowza, but I don't see it in the headers
        else:
            resp = requests.get(url)
            resp.raise_for_status()
            content = resp.content
            encoding = resp.encoding
        if encoding is None:
            raise ValueError(f'Missing encoding in response to GET {url}')
        return content.decode(encoding)
