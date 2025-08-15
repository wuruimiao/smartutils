from typing import Awaitable, Optional, Protocol, TypeVar, Union, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ConditionContainerProtocol(Protocol[T]):
    def get(
        self, block: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Union[Optional[T], Awaitable[Optional[T]]]: ...

    def put(
        self,
        value: T,
        block: bool = True,
        timeout: Optional[Union[float, int]] = None,
    ) -> Union[bool, Awaitable[bool]]: ...

    def empty(self) -> bool: ...

    def full(self) -> bool: ...

    def qsize(self) -> int: ...


# from queue import Queue

# print(isinstance(Queue(), ConditionContainerProtocol))

# from asyncio import Queue

# print(isinstance(Queue(), ConditionContainerProtocol))
