from typing import Optional, Protocol, TypeVar, Union, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ConditionContainerProtocol(Protocol[T]):
    def get(self, timeout: Union[float, int], block: bool = True) -> Optional[T]: ...

    def put(self, value: T, timeout: Union[float, int], block: bool = True) -> bool: ...


@runtime_checkable
class AsyncConditionContainerProtocol(Protocol[T]):
    async def get(
        self, timeout: Union[float, int], block: bool = True
    ) -> Optional[T]: ...

    async def put(
        self, value: T, timeout: Union[float, int], block: bool = True
    ) -> bool: ...


# import queue

# print(isinstance(queue.Queue(), ConditionContainerProtocol))
# print(isinstance(queue.Queue(), AsyncConditionContainerProtocol))
