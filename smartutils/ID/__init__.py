from smartutils.ID.init import IDGen
from smartutils.ID.const import IDGenType

__all__ = ["IDGen", "IDGenType"]

from smartutils.ID import gens
from smartutils.call import register_package

register_package(gens)
