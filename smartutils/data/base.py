import hashlib
import json
import re
import sys
from ast import literal_eval
from collections import OrderedDict
from typing import List, Mapping, Dict, Any, Union

from smartutils.data.cnnum import cn2num

__all__ = [
    "max_int",
    "min_int",
    "make_parent",
    "make_children",
    "is_num",
]
_IntReg = re.compile(r"\d+")
_ChineseNumReg = re.compile("[一二三四五六七八九十百千万]+")


# int


def max_int() -> int:
    return sys.maxsize


def min_int() -> int:
    return -sys.maxsize


def is_num(s) -> bool:
    return isinstance(s, int) or isinstance(s, float) or s.replace(".", "", 1).isdigit()


# str
def md5(text: str) -> str:
    encode_pwd = text.encode()
    md5_pwd = hashlib.md5(encode_pwd)
    return md5_pwd.hexdigest()


def trans_str(s: str) -> Any:
    """
    尝试用 literal_eval 将字符串解析为 Python 对象。
    如果解析失败，则原样返回输入。
    """
    if not isinstance(s, str):
        return s
    try:
        return literal_eval(s)
    except (ValueError, SyntaxError):
        return s


def str_to_int(s: str):
    m = md5(s)
    return int(m, 16)


def get_ints_in_str(s: str) -> list[int]:
    ss = _IntReg.findall(s)
    result = []
    for s in ss:
        if is_num(s):
            result.append(int(s))
    return result


def get_ch_num_in_str(s: str) -> list[str]:
    chinese_number_matches = _ChineseNumReg.findall(s)
    return chinese_number_matches


def chinese_to_int(chinese_number) -> Union[int, float]:
    return cn2num(chinese_number)


# dict


def dict_json(d, sort=False) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=sort)


def merge_dict(a: dict, b: dict, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dict(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def decode_bytes(b: bytes) -> tuple[str, bool]:
    try:
        return b.decode("utf-8"), True
    except UnicodeDecodeError:
        return "", False


# list
def remove_list_duplicate(data: list):
    return list(OrderedDict.fromkeys(data))


def remove_list_dup_save_first(data: list):
    exist = set()
    result = [exist.add(item) or item for item in data if item not in exist]
    return result


def make_parent(
    data: List[Mapping], info_cls, data_key: str = "id", parent_key: str = "parent_id"
) -> Dict:
    """
    构建树形结构，将数据列表按父子关系组织成多叉树。

    Args:
        data (List[Mapping]): 输入的数据列表，每个元素为一个映射（如 dict），应包含主键和父键。
        info_cls: 用于实例化每个节点的数据类或对象，支持以 **row 方式初始化。
        data_key (str): 主键字段名，默认为 "id"。
        parent_key (str): 父节点字段名，默认为 "parent_id"。

    Returns:
        Dict: 顶层节点的字典（以主键为 key），每个节点应包含 children 属性（列表），子节点挂载在其下。
    """
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
    """
    构建每个节点的祖先路径（从根到当前节点）。

    Args:
        data (List[Mapping]): 输入的数据列表，每个元素为一个映射（如 dict），应包含主键和父键。
        info_cls: 用于实例化每个节点的数据类或对象，支持以 **row 方式初始化。
        data_key (str): 主键字段名，默认为 "id"。
        parent_key (str): 父节点字段名，默认为 "parent_id"。

    Returns:
        Dict[int, List]: 每个节点 id 映射到该节点的祖先路径（List），路径顺序为 [根, ..., 当前节点]。
    """
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
