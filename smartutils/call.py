import importlib
import inspect
import pkgutil
import types

__all__ = ["call_hook", "register_package"]


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
