from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Type

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
    RouteMiddlewareFactory,
)
from smartutils.app.const import AppKey, RunEnv
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.app.plugin.log import LogPlugin
from smartutils.config.const import ConfKey
from smartutils.config.schema.middleware import MiddlewareConf
from smartutils.design import MyBase, SingletonMeta
from smartutils.error.sys import LibraryUsageError
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger


class MiddlewareManager(LibraryCheckMixin, MyBase, metaclass=SingletonMeta):
    ROUTE_APP_KEY = "app"

    def __init__(self, conf: Optional[MiddlewareConf] = None):
        self.check(conf=conf)

        self._app_key: AppKey = RunEnv.get_app()
        self._conf: MiddlewareConf = conf
        self._enable_plugins: Dict[str, List[Type[AbstractMiddlewarePlugin]]] = (
            defaultdict(list)
        )
        self._app_inited: bool = False
        if not self._conf.routes:
            return

        for key, enables in self._conf.routes.items():
            for plugin_name, plugin_cls in MiddlewarePluginFactory.all():
                if plugin_name in enables:
                    self._enable_plugins[key].append(plugin_cls)

    def _get_route_enable_plugins(
        self, route_key: str
    ) -> Tuple[AbstractMiddlewarePlugin]:
        plugins = []
        for plugin_cls in self._enable_plugins.get(route_key, []):
            plugin = plugin_cls(conf=self._conf.safe_setting)
            logger.debug(
                f"{self.name} enable plugin {plugin.key} for route {route_key}."
            )
            plugins.append(plugin)
        return tuple(plugins)

    # TODO: 其他框架的中间件执行顺序和添加顺序
    def init_app(self, app):
        if self._app_inited:
            raise LibraryUsageError(
                f"{self.name} Cannot init middleware for app key {self._app_key} twice."
            )
        self._app_inited = True

        logger.info("{name} inited in app.", name=self.name)
        AddMiddlewareFactory.get(self._app_key)(
            app, self._get_route_enable_plugins(self.ROUTE_APP_KEY)
        )

    def init_route(self, route_key: str):
        logger.info(
            "{name} inited in route {route_key}.", name=self.name, route_key=route_key
        )
        return RouteMiddlewareFactory.get(self._app_key)(
            self._get_route_enable_plugins(route_key)
        )

    def init_default_route(self):
        logger.info("{name} init default route.", name=self.name)
        return RouteMiddlewareFactory.get(self._app_key)(
            (LogPlugin(conf=self._conf.safe_setting),)
        )


@InitByConfFactory.register(ConfKey.MIDDLEWARE)
def _(conf: MiddlewareConf):
    MiddlewareManager(conf)
