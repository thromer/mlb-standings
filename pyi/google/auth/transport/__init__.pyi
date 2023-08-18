import abc
# from _typeshed import Incomplete

# TOO_MANY_REQUESTS: int
# DEFAULT_RETRYABLE_STATUS_CODES: Incomplete
# DEFAULT_REFRESH_STATUS_CODES: Incomplete
# DEFAULT_MAX_REFRESH_ATTEMPTS: int

# class Response(metaclass=abc.ABCMeta):
#     @property
#     @abc.abstractmethod
#     def status(self): ...
#     @property
#     @abc.abstractmethod
#     def headers(self): ...
#     @property
#     @abc.abstractmethod
#     def data(self): ...

class Request(metaclass=abc.ABCMeta):
    pass
#     @abc.abstractmethod
#     def __call__(self, url, method: str = ..., body: Incomplete | None = ..., headers: Incomplete | None = ..., timeout: Incomplete | None = ..., **kwargs): ...
