from dataclasses import is_dataclass
from typing import Callable, Optional, Type, TypeVar, Union

import orjson

from smartutils.error.sys import LibraryUsageError

EncodableT = TypeVar("EncodableT", bound="Encodable")


def to_json(
    data, sort=True, indent_2=False, trans_dataclass: Optional[Callable] = None
) -> bytes:
    """
    将字典数据序列化为 JSON 格式的 bytes。

    参数说明：
    :param data:         要序列化的字典对象，可以包含 int/str 类型的 key，以及 UUID 等特殊对象
    :param sort:         是否按 key 排序输出，默认为 True，便于可预测性和对比
    :param indent_2:     是否进行易读的缩进，每层缩进 2 个空格，默认为 True

    orjson 选项说明：
    - OPT_NON_STR_KEYS:      支持非字符串类型的字典 key（如 int），会自动转换为 str
    - OPT_SERIALIZE_UUID:    支持 UUID 类型自动转换为字符串格式
    - OPT_INDENT_2:          （可选）使输出 JSON 格式化，每层缩进 2 个空格
    - OPT_SORT_KEYS:         （可选）将 key 排序后输出 JSON，提高一致性

    返回值：
    - 返回序列化后的 bytes 类型 JSON 字符串

    示例：
        d = {99: {"name": "abc"}, "uid": uuid.uuid4()}
        b = dict2json(d, sort=True, indent_2=False)

    """
    options = (
        orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_UUID | orjson.OPT_SERIALIZE_NUMPY
    )
    if indent_2:
        options = options | orjson.OPT_INDENT_2
    if sort:
        options = options | orjson.OPT_SORT_KEYS
    default = None
    if trans_dataclass:
        default = trans_dataclass
        options = options | orjson.OPT_PASSTHROUGH_DATACLASS
    else:
        options = options | orjson.OPT_SERIALIZE_DATACLASS
    return orjson.dumps(data, option=options, default=default)


class Encodable:
    def encode(self) -> bytes:
        if not is_dataclass(self):
            raise LibraryUsageError("Subclasses of Encodable must be dataclasses.")
        return to_json(self)

    @classmethod
    def decode(cls: Type[EncodableT], val: Union[bytes, str]) -> EncodableT:
        d = orjson.loads(val)
        return cls(**d)


def merge_dict(a: dict, b: dict, path=None):
    """
    递归合并字典 b 到字典 a，在遇到相同 key 且 value 均为 dict 时进行递归合并，否则用 b 的值覆盖 a。
    修改在 a 上进行，并返回合并后的字典。

    参数说明：
    :param a:     目标字典，会被直接修改
    :param b:     源字典，内容合并进 a
    :param path:  递归合并时的 key 路径（用于调试、追踪），用户一般不需要传

    合并规则：
    - 若 key 仅在 b 中，添加到 a。
    - 若 key 同时存在且双方的值均为 dict，则递归合并。
    - 否则用 b[key] 覆盖 a[key]。
    - 本函数为原地修改（in-place）。

    返回值：
    - 返回合并结果（即已被修改的 a）

    示例：
        a = {'x': 1, 'y': {'z': 2}}
        b = {'y': {'z': 99, 'w': 3}, 'k': 4}
        merge_dict(a, b)
        # 结果: {'x': 1, 'y': {'z': 99, 'w': 3}, 'k': 4}
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                # 递归合并子字典
                merge_dict(a[key], b[key], path + [str(key)])
            else:
                # 不等则覆盖（允许 None/False 等“等价”情况下不覆盖）
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def decode_bytes(b: bytes) -> tuple[str, bool]:
    try:
        return b.decode("utf-8"), True
    except UnicodeDecodeError:
        return "", False
