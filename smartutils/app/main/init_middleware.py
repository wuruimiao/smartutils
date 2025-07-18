from typing import List, Optional, Tuple

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.middleware.factory import AddMiddlewareFactory
from smartutils.app.const import AppKey
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config import Config
from smartutils.config.const import ConfKey
from smartutils.config.schema.middleware import MiddlewareConf
from smartutils.log import logger


# TODO: 其他框架的中间件执行顺序和添加顺序
def init_middlewares(app, key: AppKey, reverse: bool = True):
    middleware_conf: Optional[MiddlewareConf] = Config.get_config().get(
        ConfKey.MIDDLEWARE
    )

    if not middleware_conf:
        logger.info("Middleware app init nothing for no conf.")
        return

    plugins = MiddlewarePluginFactory.all()
    if reverse:
        plugins.reverse()

    app_enable_plugins: List[Tuple[str, AbstractMiddlewarePlugin]] = []
    for plugin_name, plugin_cls in plugins:
        if plugin_name not in middleware_conf.app:
            logger.debug(f"Middleware app {plugin_name} ignored.")
        else:
            app_enable_plugins.append(
                (plugin_name, plugin_cls(key, middleware_conf.safe_setting))
            )
            logger.info(f"Middleware app {plugin_name} inited.")

    AddMiddlewareFactory.get(key)(app, app_enable_plugins)
