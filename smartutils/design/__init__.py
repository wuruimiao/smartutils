from smartutils.design._class import MyBase
from smartutils.design._singleton import SingletonBase, SingletonMeta, singleton
from smartutils.design.attr import RequireAttrs
from smartutils.design.deprecated import deprecated
from smartutils.design.factory import BaseFactory
from smartutils.design.module import require_modules
from smartutils.design.wrapper.proxy import proxy_wrapper

__all__ = [
    "singleton",
    "SingletonBase",
    "SingletonMeta",
    "deprecated",
    "BaseFactory",
    "RequireAttrs",
    "require_modules",
    "MyBase",
    "proxy_wrapper",
]
