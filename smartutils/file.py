import sys
from typing import Dict

import yaml

from smartutils.log import logger
from smartutils.ret.exc import FileError
from smartutils.call import exit_on_fail


def load_yaml(filepath: str, exit_on_err: bool = True) -> Dict:
    try:
        with open(filepath) as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, PermissionError, yaml.YAMLError) as e:
        msg = f"yaml file {filepath} load fail: {e}"
        logger.exception(msg)
        if exit_on_err:
            exit_on_fail()
        raise FileError(msg)
