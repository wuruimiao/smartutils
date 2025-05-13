import importlib
import inspect
import pkgutil
import sys
import types

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
        importlib.import_module(modname)


def exit_on_fail():
    # 非0，k8s判定启动失败；应用在 lifespan 阶段（即启动/关闭事件）报错，uvicorn 退出码是 3
    sys.exit(1)
