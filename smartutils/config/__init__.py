import logging
from typing import Dict, Any, Optional

import yaml

from smartutils.config.factory import ConfFactory
from smartutils.config.config import ConfigObj

logger = logging.getLogger(__name__)


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._config: Dict[str, Any] = {}
        self._instances: Dict[str, Any] = {}
        self._initialized = True

    def load_conf(self, config_path: str):
        with open(config_path) as f:
            self._config = yaml.safe_load(f)
        for key, conf in self._config.items():
            logger.info(f'load conf: {key}')
            self._instances[key] = ConfFactory.create(key, conf)

    def get(self, name: str) -> Optional[Any]:
        return self._instances.get(name)


_config: ConfigObj


def init(conf_path: str = 'config/config.yaml') -> ConfigObj:
    global _config
    _c = Config()
    _c.load_conf(conf_path)
    _config = ConfigObj(_c)
    return _config


def get_config() -> ConfigObj:
    global _config
    if _config is None:
        raise RuntimeError("Config not initialized")
    return _config
