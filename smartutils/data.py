import json


def dict_json(d, sort=False) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=sort)
