from typing import Callable, List, Tuple

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddlewarePlugin,
)
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["AddMiddlewareFactory"]


class AddMiddlewareFactory(
    BaseFactory[
        AppKey, Callable[[object, List[Tuple[str, AbstractMiddlewarePlugin]]], None]
    ]
):
    pass
