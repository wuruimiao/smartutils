from typing import Awaitable, Optional, Protocol, TypeVar, Union

T = TypeVar("T")


class ResourcePoolProtocol(Protocol[T]):
    def init(self) -> Union[None, Awaitable[None]]: ...
    def acquire(
        self, timeout: Optional[Union[float, int]] = None
    ) -> Union[Optional[T], Awaitable[Optional[T]]]: ...

    def release(
        self, resource: T, timeout: Optional[Union[float, int]] = None
    ) -> Union[None, Awaitable[None]]: ...
