from smartutils.config.const import ConfKeys
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.config.init import init, get_config

__all__ = ["init", "get_config", "ConfFactory", "ConfKeys", "ProjectConf"]

from smartutils.config import schema
from smartutils.call import register_package

register_package(schema)
