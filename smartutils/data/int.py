# int


import re
import sys

_IntReg = re.compile(r"\d+")
_ChineseNumReg = re.compile("[一二三四五六七八九十百千万]+")


def max_int() -> int:
    return sys.maxsize


def min_int() -> int:
    return -sys.maxsize


def is_num(s) -> bool:
    if isinstance(s, (int, float)):
        return True
    if not isinstance(s, str):
        return False
    return s.replace(".", "", 1).isdigit()
