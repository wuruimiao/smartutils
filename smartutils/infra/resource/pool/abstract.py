from typing import Optional, Protocol, TypeVar, Union

T = TypeVar("T")


class ResourcePoolProtocol(Protocol[T]):
    def acquire(self, timeout: Optional[Union[float, int]] = None) -> Optional[T]: ...

    def release(
        self, resource: T, timeout: Optional[Union[float, int]] = None
    ) -> None: ...


class AsyncResourcePoolProtocol(Protocol[T]):
    async def acquire(
        self, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]: ...

    async def release(
        self, resource: T, timeout: Optional[Union[float, int]] = None
    ) -> None: ...
