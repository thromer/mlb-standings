from typing import final

from .typing_protocols import RateLimiterLike, WebLike


@final
class AbstractRateLimitedWeb:
    def __init__(self, web: WebLike, limiter: RateLimiterLike) -> None:
        self.web = web
        self.limiter = limiter

    def read(self, url: str) -> str:
        self.limiter.delay()
        return self.web.read(url)
