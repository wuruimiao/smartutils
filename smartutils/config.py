from typing import Dict, Any

import yaml


class Config:
    def __init__(self):
        self._config: Dict[str, Any] = {}

    def load_config(self, config_path: str):
        with open(config_path) as f:
            self._config = yaml.safe_load(f)

    @property
    def config(self):
        return self._config

    @property
    def logging(self) -> Dict:
        return self._config['logging']

    @property
    def mysql(self) -> Dict[str, Any]:
        return self._config['mysql']

    @property
    def redis(self) -> Dict[str, Any]:
        return self._config['redis']

    @property
    def kafka(self) -> Dict[str, Any]:
        return self._config['kafka']

    @property
    def canal(self) -> Dict[str, Any]:
        return self._config['canal']


config = Config()


def init(conf_path: str = 'config/config.yaml'):
    config.load_config(conf_path)
