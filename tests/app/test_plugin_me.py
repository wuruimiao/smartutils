import pytest

from smartutils.config.schema.middleware import (
    MiddlewarePluginSetting,
    PluginDependAuthConf,
)
from smartutils.error.sys import LibraryUsageError


def test_plugin_me_init_exception():
    from smartutils.app.plugin.me import MePlugin

    with pytest.raises(LibraryUsageError):
        MePlugin(conf=MiddlewarePluginSetting(me=PluginDependAuthConf(local=True)))
