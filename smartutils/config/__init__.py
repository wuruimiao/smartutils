from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf
from smartutils.config.init import init, get_config

from smartutils.config import schema
from smartutils.call import register_package

__all__ = ['init', 'get_config', 'ConfFactory', 'ConfKey', 'ProjectConf']

register_package(schema)
