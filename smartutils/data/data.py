import hashlib
import json
import re
import sys
import uuid
import zlib
from ast import literal_eval
from collections import OrderedDict
from dataclasses import asdict
from .pycnnum import cn2num


def format_file_name(name: str, version: int = sys.maxsize) -> str:
    """
    规范化文件名中，一些会导致显示异常的字符
    :param name:
    :param version: 1原样 2替换|/\\
    :return:
    """
    if version == 1:
        return name

    name = name.replace("|", "_").replace("/", "").replace("\\", "")
    if version <= 2:
        return name

    # 版本3除了下面替换，还有最后的去空格和_
    if version >= 3:
        name = name.replace("\n", " ").replace("\r\n", " ")
        # -不能换成_
        name = name.replace("……", "_").replace('"', "_").replace("'", "_") \
            .replace("！", " ").replace("!", " ") \
            .replace(",", " ").replace(".", " ") \
            .replace("，", " ").replace("。", " ") \
            .replace("[", " ").replace("]", " ") \
            .replace("【", " ").replace("】", " ")

    if version >= 4:
        name = name.replace("(", " ").replace(")", " ") \
            .replace("~", " ") \
            .replace("&", " ") \
            .replace("$", " ") \
            .replace("=", " ")

    if version >= 5:
        name = name.replace(":", " ").replace("*", " ").replace("?", " ") \
            .replace("<", " ").replace(">", " ")

    name = name.strip()
    name = ' '.join(name.split())
    name = name.replace(" ", "_")
    return name


linux_illegal = ('/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.', ' ')
windows_illegal = ('<', '>', ':', '"', '/', '\\', '|', '?', '*')


def sanitize_filename(name: str, linux: bool = True, windows: bool = True):
    """
    格式化文件名非法字符
    :param name:
    :param linux:
    :param windows:
    :return:
    """
    replace_char = "_"
    if linux:
        for char in linux_illegal:
            name = name.replace(char, replace_char)
    if windows:
        for char in windows_illegal:
            name = name.replace(char, replace_char)
        name = name.rstrip(". ")

    return name


def md5(text):
    encode_pwd = text.encode()
    md5_pwd = hashlib.md5(encode_pwd)
    return md5_pwd.hexdigest()


def str_to_int(s: str):
    m = md5(s)
    return int(m, 16)


def is_num(s) -> bool:
    return isinstance(s, int) or isinstance(s, float) or s.replace('.', '', 1).isdigit()


def uniq_id() -> str:
    return uuid.uuid1().hex


def decode_gzip(b: bytes) -> bytes:
    try:
        return zlib.decompress(b, 16 + zlib.MAX_WBITS)
    except zlib.error:
        return b


def decode_bytes(b: bytes) -> tuple[str, bool]:
    try:
        return b.decode("utf-8"), True
    except UnicodeDecodeError:
        return "", False


class LowStr(str):
    def __new__(cls, s: str):
        return str.__new__(cls, s.lower())


def get_first_by_order(data, order: tuple):
    for o in order:
        if o in data:
            return o
    return None


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


def trans_str(s: str):
    try:
        return literal_eval(s)
    except Exception:
        return s


def remove_list_duplicate(data: list):
    return list(OrderedDict.fromkeys(data))


def remove_list_dup_save_first(data: list):
    exist = set()
    result = [exist.add(item) or item for item in data if item not in exist]
    return result


def dict_json(d) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=True)


class Data:
    def dict(self):
        return asdict(self)

    def __str__(self):
        return dict_json(self.dict())

    @classmethod
    def parse(cls, s: str):
        return cls(**json.loads(s))

    @classmethod
    def parse_dict(cls, d: dict):
        if not isinstance(d, dict):
            return d
        return cls(**d)


_ChNumReg = re.compile('[一二三四五六七八九十百千万]+')  # Chinese number character pattern


def get_ch_num_in_str(s: str) -> list[str]:
    chinese_number_matches = _ChNumReg.findall(s)
    return chinese_number_matches


_IntReg = re.compile(r'\d+')


def get_ints_in_str(s: str) -> list[int]:
    ss = _IntReg.findall(s)
    result = []
    for s in ss:
        if is_num(s):
            result.append(int(s))
    return result


def chinese_to_int(chinese_number):
    return cn2num(chinese_number)


def first_bigger_in_increase(target, data, key=None):
    """
    在递增序列data中，找到第一个比target大的，也是list.insert应该插入的位置
    list.insert，i位替代，原i及之后，依次往后挪一位
    """
    for i in range(len(data) - 1, -1, -1):
        item = data[i]
        if key:
            item = key(item)
        if item is None:
            # 如果中间有None，无法比较，那就插入到它后面
            return i + 1
        if item > target:
            continue
        # 第1个小于等于target的，返回其后一个
        return i + 1
    return 0


def extract_first_number(s: str) -> int:
    num = get_ints_in_str(s)
    if not num:
        num = get_ch_num_in_str(s)

    if num:
        num = num[0]
        if isinstance(num, str):
            num = chinese_to_int(num)
    else:
        num = None
    return num
