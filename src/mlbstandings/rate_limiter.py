import time
from typing import final


@final
class SimpleRateLimiter:
    def __init__(self, period: float) -> None:
        self.period = period

    def delay(self) -> None:
        print(f"sleeping {self.period}")
        time.sleep(self.period)


class NullRateLimiter:
    @staticmethod
    def delay() -> None:
        pass
