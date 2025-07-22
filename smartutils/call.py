import asyncio
import importlib
import importlib.util
import inspect
import os
import pkgutil
import sys
import types
from contextlib import contextmanager

__all__ = [
    "call_hook",
    "register_package",
    "exit_on_fail",
    "installed",
    "mock_module_absent",
]


async def call_hook(hook, *args, **kwargs):
    if hook is None:
        return

    result = hook(*args, **kwargs)
    if inspect.isawaitable(result):
        await result


def call_async(func):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(func)


def register_package(package: types.ModuleType):
    """
    自动递归扫描并import package下所有模块（包括子包），从而触发注册。
    """
    for finder, modname, ispkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        # try:
        importlib.import_module(modname)
        # except ImportError as e:
        # logger.debug("register_package fail: {e}", e=e)


def installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def mock_module_absent(monkeypatch, module_name: str):
    """临时移除sys.modules中的某个模块（模拟未安装场景）"""
    monkeypatch.setitem(sys.modules, module_name, None)


def exit_on_fail():
    # 非0，k8s判定启动失败；应用在 lifespan 阶段（即启动/关闭事件）报错，uvicorn 退出码是 3
    os._exit(1)  # noqa


@contextmanager
def mock_dbcli(mocker, patch_target):
    """
    通用patch Manager依赖db client的上下文管理器。
    用法：
        with mock_dbcli(mocker, ...) as (MockDBCli, fake_session, instance):
            # ...测试体...
    """
    MockDBCli = mocker.patch(patch_target)
    fake_session = mocker.AsyncMock()
    fake_session.commit = mocker.AsyncMock()
    fake_session.rollback = mocker.AsyncMock()
    fake_session.in_transaction = mocker.MagicMock(return_value=True)

    async_context_mgr = mocker.AsyncMock()
    async_context_mgr.__aenter__.return_value = (fake_session, None)
    async_context_mgr.__aexit__.return_value = None

    instance = MockDBCli.return_value
    instance.db.return_value = async_context_mgr
    instance.close = mocker.AsyncMock()

    yield MockDBCli, fake_session, instance
