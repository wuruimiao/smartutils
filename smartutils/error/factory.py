from typing import Type, Callable

from smartutils.design import BaseFactory
from smartutils.error.base import BaseError
from smartutils.error.sys_err import SysError

__all__ = ["ExcFactory"]


class ExcFactory(BaseFactory[Type[BaseException], Callable[[BaseException], BaseError]]):
    @classmethod
    def get(cls, key: BaseException) -> BaseError:
        if isinstance(key, BaseError):
            return key

        for ext_type, handler in cls._registry.items():
            if isinstance(key, ext_type):
                return handler(key)

        return SysError(detail=str(key))
