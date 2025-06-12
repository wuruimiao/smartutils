from typing import Type

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.const import MiddlewarePluginKey
from smartutils.design import BaseFactory

__all__ = ["MiddlewarePluginFactory"]


class MiddlewarePluginFactory(
    BaseFactory[MiddlewarePluginKey, Type[AbstractMiddlewarePlugin]]
):
    pass
