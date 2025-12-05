import contextvars
import sys
from contextlib import contextmanager
from typing import Any

from smartutils.ctx.const import CTXKey
from smartutils.design import BaseFactory
from smartutils.error.sys import LibraryUsageError

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["CTXVarManager"]


class CTXVarManager(BaseFactory[CTXKey, contextvars.ContextVar, None]):
    _default_v_constructor = staticmethod(contextvars.ContextVar)

    @classmethod
    @contextmanager
    def use(cls, key: CTXKey, value: Any):
        # 嵌套场景下，内层 value 会临时覆盖 contextvar 的 value，内层退出后自动恢复外层 value
        # 增加is_first，嵌套场景下，都是同一个value

        var = super(CTXVarManager, cls).get(key)
        is_first = False
        try:
            var.get()
        except LookupError:
            is_first = True

        if is_first:
            token = var.set(value)
            try:
                yield
            finally:
                var.reset(token)
        else:
            yield

    @classmethod
    @override
    def get(cls, key: CTXKey, default: Any = None, return_none: bool = False) -> Any:
        try:
            var = super(CTXVarManager, cls).get(key)
            return var.get()
        except (LookupError, LibraryUsageError):
            if default is not None:
                return default

            if return_none:
                return None

            raise LibraryUsageError(
                f"Must call CTXVarManager.use({key}) first."
            ) from None
