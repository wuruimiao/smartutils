from collections import defaultdict
from typing import Dict, List, Optional, Type

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
    RouteMiddlewareFactory,
)
from smartutils.app.const import AppKey
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.app.plugin.log import LogPlugin
from smartutils.config.const import ConfKey
from smartutils.config.schema.middleware import MiddlewareConf
from smartutils.design import SingletonMeta
from smartutils.error.sys import LibraryUsageError
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

_ROUTE_APP_KEY = "app"


class MiddlewareManager(LibraryCheckMixin, metaclass=SingletonMeta):
    def __init__(self, conf: Optional[MiddlewareConf] = None):
        self.check(conf=conf)

        self._app_key: AppKey
        self._conf: MiddlewareConf = conf
        self._enable_plugins: Dict[str, List[Type[AbstractMiddlewarePlugin]]] = (
            defaultdict(list)
        )
        if not self._conf.routes:
            return

        for key, enables in self._conf.routes.items():
            for plugin_name, plugin_cls in MiddlewarePluginFactory.all():
                if plugin_name in enables:
                    self._enable_plugins[key].append(plugin_cls)

    def _get_route_enable_plugins(
        self, route_key: str, key: AppKey
    ) -> List[AbstractMiddlewarePlugin]:
        plugins = []
        for plugin_cls in self._enable_plugins.get(route_key, []):
            plugin = plugin_cls(key, self._conf.safe_setting)
            logger.debug(f"Enable plugin {plugin.key} for route {route_key}.")
            plugins.append(plugin)
        return plugins

    # TODO: 其他框架的中间件执行顺序和添加顺序
    def init_app_middlewares(self, app, app_key: AppKey):
        if hasattr(self, "_app_key"):
            raise LibraryUsageError(
                "Cannot init middleware for app key {app_key} twice."
            )
        self._app_key = app_key

        logger.info("Middleware inited in app.")
        AddMiddlewareFactory.get(app_key)(
            app, self._get_route_enable_plugins(_ROUTE_APP_KEY, app_key)
        )

    def init_route_middleware(self, route_key: str):
        logger.info(f"Middleware inited in route {route_key}.")
        return RouteMiddlewareFactory.get(self._app_key)(
            self._get_route_enable_plugins(route_key, self._app_key)
        )

    def init_default_route_middleware(self):
        logger.info("Middleware init default route.")
        return RouteMiddlewareFactory.get(self._app_key)(
            [LogPlugin(self._app_key, self._conf.safe_setting)]
        )


@InitByConfFactory.register(ConfKey.MIDDLEWARE)
def _(conf: MiddlewareConf):
    MiddlewareManager(conf)
