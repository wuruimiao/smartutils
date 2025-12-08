from typing import Type

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.design import BaseFactory

__all__ = ["MiddlewarePluginFactory"]


class MiddlewarePluginFactory(
    BaseFactory[MiddlewarePluginKey, Type[AbstractMiddlewarePlugin], None]
):
    """
    管理：不同应用框架下，如何构造对应的中间件插件类，以在应用中统一添加中间件插件。
    """

    ...
