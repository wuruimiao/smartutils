import sys

from smartutils.design.factory_mixin import TypeDispatchBaseFactory
from smartutils.error.base import BaseError
from smartutils.error.sys import SysError

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override
__all__ = ["ExcErrorFactory", "ExcDetailFactory"]


class ExcErrorFactory(TypeDispatchBaseFactory[BaseException, BaseError, None]):
    """
    管理：“转换”异常为自定义BaseError的方法
    如：将PydanticValidationError转换为ValidationError，并提取detail信息
    通过注册不同的“异常类型及其转换”方法，实现对各种“异常”的统一处理
    """

    @classmethod
    @override
    def v_type(cls) -> type[BaseError]:
        return BaseError

    @classmethod
    @override
    def default(cls, key: BaseException) -> BaseError:
        raise SysError(detail=str(key))


class ExcDetailFactory(TypeDispatchBaseFactory[BaseException, str, None]):
    """
    管理：“提取”异常信息，组成detail字符串的方法
    如：将PydanticValidationError中的错误信息提取并格式化为字符串
    通过注册不同的“异常类型及其提取”方法，实现对各种“异常信息”的统一处理
    """

    @classmethod
    @override
    def v_type(cls) -> type[str]:
        return str

    @classmethod
    @override
    def default(cls, key: BaseException) -> str:
        return str(key)
