from collections import defaultdict
from typing import Dict, List, Optional, OrderedDict, Tuple

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
    EndpointMiddlewareFactory,
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
from smartutils.log import logger


class MiddlewareManager(MyBase, metaclass=SingletonMeta):
    ROUTE_APP_KEY = "app"

    def __init__(self, conf: Optional[MiddlewareConf] = None):
        if not conf:
            logger.info(
                "{name} get none conf, no middleware will be added.", name=self.name
            )
            conf = MiddlewareConf()

        self._app_key: AppKey = RunEnv.get_app()
        assert self._app_key, f"{self.name} should call RunEnv.set_app() first."
        self._conf: MiddlewareConf = conf
        self._route_ps: Dict[str, List[AbstractMiddlewarePlugin]] = self._init_route()
        self._app_inited: bool = False

    def _init_route(self) -> Dict:
        if not self._conf.routes:
            return {}

        all_enables = {name for v in self._conf.routes.values() for name in v}
        plugins = OrderedDict()  # 兼容3.7以下
        for plugin_name, plugin_cls in MiddlewarePluginFactory.all():
            if plugin_name in all_enables:
                plugins[plugin_name] = plugin_cls(conf=self._conf.safe_setting)

        result = defaultdict(list)
        for plugin_name, plugin in plugins.items():
            for key, enables in self._conf.routes.items():
                if plugin_name in enables:
                    logger.debug(
                        "{name} enable plugin {p_key} for route {key}.",
                        name=self.name,
                        p_key=plugin.key,
                        key=key,
                    )
                    result[key].append(plugin)
        return result

    def _get_ps(self, route_key: str) -> Tuple[AbstractMiddlewarePlugin, ...]:
        if route_key not in self._route_ps:
            raise LibraryUsageError(
                f"{self.name} require {route_key} below middleware.routes in config.yaml."
            )

        return tuple(self._route_ps[route_key])

    # TODO: 其他框架的中间件执行顺序和添加顺序
    def init_app(self, app):
        if self.ROUTE_APP_KEY not in self._route_ps:
            logger.debug(
                "{name} no {key} below middleware.routes in config.yaml, ignore.",
                name=self.name,
                key=self.ROUTE_APP_KEY,
            )
            return
        if self._app_inited:
            raise LibraryUsageError(
                f"{self.name} Cannot init middleware for app key {self._app_key} twice."
            )
        self._app_inited = True

        logger.info("{name} inited in app.", name=self.name)
        AddMiddlewareFactory.get(self._app_key)(app, self._get_ps(self.ROUTE_APP_KEY))

    def init_route(self, route_key: str):
        return RouteMiddlewareFactory.get(self._app_key)(self._get_ps(route_key))

    def init_endpoint(self, route_key: str):
        logger.info(
            "{name} inited in endpoint {route_key}.",
            name=self.name,
            route_key=route_key,
        )
        return EndpointMiddlewareFactory.get(self._app_key)(self._get_ps(route_key))

    def init_default_route(self):
        logger.info("{name} init default route.", name=self.name)
        return RouteMiddlewareFactory.get(self._app_key)(
            (LogPlugin(conf=self._conf.safe_setting),)
        )


@InitByConfFactory.register(ConfKey.MIDDLEWARE)
def _(conf: MiddlewareConf):
    MiddlewareManager(conf)
