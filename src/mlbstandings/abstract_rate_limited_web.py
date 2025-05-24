from mlbstandings.typing_protocols import *
from typing import Any


class AbstractRateLimitedWeb:
    def __init__(self, web: WebLike, limiter: RateLimiterLike) -> None:
        self.web = web
        self.limiter = limiter

    def read(self, url: str, headers: dict[str, Any]={}) -> str:
        self.limiter.delay()
        return self.web.read(url, headers=headers)
