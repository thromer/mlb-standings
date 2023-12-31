import abc
# from _typeshed import Incomplete
from google.auth.transport.requests import Request

class Credentials(metaclass=abc.ABCMeta):
#     token: Incomplete
#     expiry: Incomplete
#     def __init__(self) -> None: ...
    @property
    def expired(self) -> bool : ...
    @property
    def valid(self) -> bool: ...
#     @property
#     def quota_project_id(self): ...
#     @abc.abstractmethod
    def refresh(self, request: Request) -> None: ...
#     def apply(self, headers, token: Incomplete | None = ...) -> None: ...
#     def before_request(self, request, method, url, headers) -> None: ...

class CredentialsWithQuotaProject(Credentials, metaclass=abc.ABCMeta):
    pass
#     def with_quota_project(self, quota_project_id) -> None: ...
#     def with_quota_project_from_environment(self): ...

# class CredentialsWithTokenUri(Credentials, metaclass=abc.ABCMeta):
#     def with_token_uri(self, token_uri) -> None: ...

# class AnonymousCredentials(Credentials):
#     @property
#     def expired(self): ...
#     @property
#     def valid(self): ...
#     def refresh(self, request) -> None: ...
#     def apply(self, headers, token: Incomplete | None = ...) -> None: ...
#     def before_request(self, request, method, url, headers) -> None: ...

class ReadOnlyScoped(metaclass=abc.ABCMeta):
    pass
#     def __init__(self) -> None: ...
#     @property
#     def scopes(self): ...
#     @property
#     def default_scopes(self): ...
#     @property
#     @abc.abstractmethod
#     def requires_scopes(self): ...
#     def has_scopes(self, scopes): ...

# class Scoped(ReadOnlyScoped, metaclass=abc.ABCMeta):
#     @abc.abstractmethod
#     def with_scopes(self, scopes, default_scopes: Incomplete | None = ...): ...

# def with_scopes_if_required(credentials, scopes, default_scopes: Incomplete | None = ...): ...

# class Signing(metaclass=abc.ABCMeta):
#     @abc.abstractmethod
#     def sign_bytes(self, message): ...
#     @property
#     @abc.abstractmethod
#     def signer_email(self): ...
#     @property
#     @abc.abstractmethod
#     def signer(self): ...
