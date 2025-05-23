import ipaddress
import json
import re
from enum import Enum
from typing import List, Mapping, TypeVar, Type, Dict, Any

__all__ = [
    "dict_json",
    "check_ip",
    "check_domain",
    "check_port",
    "max_int",
    "min_int",
    "make_parent",
    "make_children",

    "ZhEnumBase",
]

import sys

DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*"
    r"\.[A-Za-z]{2,}$"
)


def dict_json(d, sort=False) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=sort)


def check_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def check_domain(domain: str) -> bool:
    return not not DOMAIN_REGEX.match(domain)


def check_port(port: int) -> bool:
    return 1 <= port <= 65535


def max_int() -> int:
    return sys.maxsize


def min_int() -> int:
    return -sys.maxsize


def make_parent(
    data: List[Mapping], info_cls, data_key: str = "id", parent_key: str = "parent_id"
) -> Dict:
    node_map = {row[data_key]: info_cls(**row) for row in data}
    result = {}
    for node in node_map.values():
        parent_id = getattr(node, parent_key, 0)
        if parent_id != 0:
            parent = node_map.get(parent_id)
            if parent:
                parent.children.append(node)
            else:
                # 没找到父亲，被视为孤儿
                result[node.id] = node
        else:
            # 纯顶层
            result[node.id] = node
    return result


def make_children(
    data: List[Mapping], info_cls, data_key: str = "id", parent_key: str = "parent_id"
) -> Dict[int, List]:
    node_map = {row[data_key]: info_cls(**row) for row in data}
    result = {}

    for node_id, node in node_map.items():
        path = []
        cur = node
        while True:
            path.append(cur)
            parent_id = getattr(cur, parent_key, 0)
            if parent_id == 0 or parent_id not in node_map:
                break
            cur = node_map[parent_id]
        result[node_id] = list(reversed(path))
    return result


T = TypeVar("T", bound="ZhEnumBase")


class ZhEnumBase(Enum):
    """
    支持变量-中文双向映射的通用枚举基类。
    子类不要在类体里写映射字典，需在类外写。
    """

    @property
    def zh(self) -> str:
        return self._obj_zh_map()[self]

    @classmethod
    def from_zh(cls: Type[T], zh: str) -> T:
        return cls._zh_obj_map()[zh]

    @classmethod
    def zh_from_value(cls: Type[T], value: Any) -> str:
        return cls(value).zh

    @classmethod
    def value_from_zh(cls: Type[T], zh: str) -> Any:
        return cls.from_zh(zh).value

    @classmethod
    def zh_choices(cls: Type[T]):
        return [(e, e.zh) for e in cls]

    @classmethod
    def zh_choices_str(cls) -> str:
        return " ".join(f"{item.value}: {item.zh}" for item in cls)

    @classmethod
    def zh_list(cls: Type[T]):
        return [e.zh for e in cls]

    @staticmethod
    def _obj_zh_map() -> Dict[Any, str]:
        raise NotImplementedError("子类必须实现 _obj_zh_map 方法")

    @staticmethod
    def _zh_obj_map() -> Dict[str, Any]:
        raise NotImplementedError("子类必须实现 _zh_obj_map 方法")