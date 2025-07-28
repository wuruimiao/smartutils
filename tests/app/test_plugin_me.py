import pytest

from smartutils.app.const import AppKey, RunEnv
from smartutils.config.schema.middleware import (
    MiddlewarePluginSetting,
    PluginDependAuthConf,
)
from smartutils.error.sys import LibraryUsageError

RunEnv.set_app(AppKey.FASTAPI)


def test_plugin_me_init_no_token_helper():
    from smartutils.app.plugin.me import MePlugin

    with pytest.raises(LibraryUsageError) as exc:
        MePlugin(conf=MiddlewarePluginSetting(me=PluginDependAuthConf(local=True)))
    assert (
        str(exc.value)
        == "[MePlugin] requires token in config.yaml. err=[TokenHelper] require conf, init by infra normally."
    )


def test_plugin_me_init_no_auth_client():
    from smartutils.app.plugin.me import MePlugin

    with pytest.raises(LibraryUsageError) as exc:
        MePlugin(conf=MiddlewarePluginSetting(me=PluginDependAuthConf(local=False)))
    assert str(exc.value) == "[MePlugin] requires auth below client in config.yaml."
