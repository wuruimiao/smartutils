import importlib
import inspect
import os
import pkgutil
import types

from smartutils.log import logger

__all__ = ["call_hook", "register_package", "exit_on_fail"]


async def call_hook(hook, *args, **kwargs):
    if hook is None:
        return

    result = hook(*args, **kwargs)
    if inspect.isawaitable(result):
        await result


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


def exit_on_fail():
    # 非0，k8s判定启动失败；应用在 lifespan 阶段（即启动/关闭事件）报错，uvicorn 退出码是 3
    os._exit(1)  # noqa
