from typing import Type, Callable

from smartutils.design import BaseFactory
from smartutils.error.base import BaseError
from smartutils.error.sys_err import SysError

__all__ = ["ExcFactory", "ExcFormatFactory"]


class ExcFactory(BaseFactory[Type[BaseException], Callable[[BaseException], BaseError]]):
    @classmethod
    def get(cls, exc: BaseException) -> BaseError:
        if isinstance(exc, BaseError):
            return exc

        for ext_type, handler in cls._registry.items():
            if isinstance(exc, ext_type):
                return handler(exc)

        return SysError(detail=str(exc))


class ExcFormatFactory(BaseFactory[Type[BaseException], Callable[[BaseException], str]]):
    @classmethod
    def get(cls, exc: BaseException) -> str:
        for ext_type, handler in cls._registry.items():
            if isinstance(exc, ext_type):
                return handler(exc)

        return str(exc)
