from typing import Dict

import yaml

from smartutils.ret.exc import FileError


def load_yaml(filepath: str) -> Dict:
    try:
        with open(filepath) as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, PermissionError, yaml.YAMLError) as e:
        raise FileError(f"yaml file {filepath} load fail")
