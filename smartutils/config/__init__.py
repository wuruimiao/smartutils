from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.init import init, get_config
from smartutils.config.schema.project import ProjectConf

__all__ = ["init", "get_config", "ConfFactory", "ConfKey", "ProjectConf"]

from smartutils.config import schema
from smartutils.call import register_package

register_package(schema)
