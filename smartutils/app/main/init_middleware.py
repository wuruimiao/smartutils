from smartutils.app.adapter.middleware.factory import AddMiddlewareFactory
from smartutils.app.const import AppKey
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.log import logger


def init_middlewares(app, key: AppKey):
    for plugin_name, plugin_cls in MiddlewarePluginFactory.all():
        AddMiddlewareFactory.get(key)(app, plugin_cls(key))
        logger.info(f"Middleware {plugin_name} inited.")
