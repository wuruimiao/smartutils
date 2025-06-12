from smartutils.design.attr import RequireAttrs
from smartutils.design.deprecated import deprecated
from smartutils.design.factory import BaseFactory
from smartutils.design.module import require_modules
from smartutils.design.singleton import SingletonBase, SingletonMeta, singleton

__all__ = [
    "singleton",
    "SingletonBase",
    "SingletonMeta",
    "deprecated",
    "BaseFactory",
    "RequireAttrs",
    "require_modules",
]
