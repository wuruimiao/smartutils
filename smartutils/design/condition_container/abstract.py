from typing import Optional, Protocol, TypeVar, Union, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ConditionContainerProtocol(Protocol[T]):
    def get(
        self, blocking: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]: ...

    def put(
        self,
        value: T,
        blocking: bool = True,
        timeout: Optional[Union[float, int]] = None,
    ) -> bool: ...

    def empty(self) -> bool: ...


@runtime_checkable
class AsyncConditionContainerProtocol(Protocol[T]):
    async def get(
        self, blocking: bool = True, timeout: Optional[Union[float, int]] = None
    ) -> Optional[T]: ...

    async def put(
        self,
        value: T,
        blocking: bool = True,
        timeout: Optional[Union[float, int]] = None,
    ) -> bool: ...

    def empty(self) -> bool: ...


# from queue import Queue

# print(isinstance(Queue(), ConditionContainerProtocol))
# print(isinstance(Queue(), AsyncConditionContainerProtocol))

# from asyncio import Queue

# print(isinstance(Queue(), ConditionContainerProtocol))
# print(isinstance(Queue(), AsyncConditionContainerProtocol))
