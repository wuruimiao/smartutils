from typing import Optional

from smartutils.app.adapter.middleware.factory import AddMiddlewareFactory
from smartutils.app.const import AppKey
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config import get_config
from smartutils.config.const import ConfKey
from smartutils.config.schema.middleware import MiddlewareConf
from smartutils.log import logger


def init_middlewares(app, key: AppKey, reverse: bool = True):
    middleware_conf: Optional[MiddlewareConf] = get_config().get(ConfKey.MIDDLEWARE)

    if not middleware_conf:
        logger.info("Middleware app init nothing for no conf.")
        return

    enables = middleware_conf.app
    plugins = MiddlewarePluginFactory.all()
    if reverse:
        plugins.reverse()
    for plugin_name, plugin_cls in plugins:
        if plugin_name not in enables:
            logger.debug(f"Middleware app {plugin_name} ignored.")
        else:
            AddMiddlewareFactory.get(key)(
                app, plugin_cls(key, middleware_conf.safe_setting), plugin_name
            )
            logger.info(f"Middleware app {plugin_name} inited.")
