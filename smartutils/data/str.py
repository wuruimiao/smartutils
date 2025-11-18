# str
import hashlib
from ast import literal_eval
from typing import Any, Union

from smartutils.data.cnnum import cn2num
from smartutils.data.int import _ChineseNumReg, _IntReg, is_num


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
