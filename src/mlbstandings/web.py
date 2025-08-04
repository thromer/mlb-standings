import urllib.error

# TODO: remove once we're running on a system that works with urllib3 + baseball-reference.com
import urllib.request  # import Request, urlopen
from typing import override

import backoff
import requests

from mlbstandings.typing_protocols import WebLike


class Web(WebLike):
    @staticmethod
    def retryable(code: int) -> bool:
        return code in {429, 500, 503}

    @staticmethod
    def giveup(e: Exception) -> bool:
        if isinstance(e, requests.exceptions.HTTPError):
            code = e.response.status_code
        elif isinstance(e, urllib.error.HTTPError):
            code = e.code
        else:
            return False
        return not Web.retryable(code)

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.HTTPError,
            urllib.error.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ),
        max_time=600,
        giveup=lambda e: Web.giveup(e),
        max_value=60,
    )
    @override
    def read(self, url: str) -> str:
        if url.startswith("https://www.baseball-reference.com/"):
            print(f"Using urllib in Web.read({url})")
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                return resp.read().decode("ISO-8859-1")
        print(f"Using requests in Web.read({url})")
        r = requests.get(url)
        r.raise_for_status()
        if r.encoding is None:
            msg = f"Missing encoding in esponse to GET {url}"
            raise ValueError(msg)
        return r.content.decode(r.encoding)
