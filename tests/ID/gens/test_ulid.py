from datetime import datetime

import pytest
from ulid import ULID as LibULID

from smartutils.ID.gens.ulid import ULID, ULIDGenerator


def make_ulid(ts_ms=1685596800000, rnd=0):
    # 构造一个ulid对象（ulid库标准）: 48 bit ts + 80 bit rnd
    value = (ts_ms << 80) | rnd
    return LibULID(value.to_bytes(16, "big"))


def test_ulid_from_str():
    ulid_obj = make_ulid(1685596800000, 12345)
    ustr = str(ulid_obj)
    u = ULID(ustr)
    assert u.timestamp == 1685596800000
    assert u.milliseconds == 1685596800000
    # 12345 十六进制是 3039
    assert u.random_hex.endswith("3039")
    assert isinstance(u.datetime, datetime)
    assert u.value == int(ulid_obj)
    assert u.__repr__().startswith("ULID(")
    # parse classmethod
    assert ULID.parse(ulid_obj).timestamp == 1685596800000


def test_ulid_from_ulid_obj():
    ulid_obj = make_ulid(1, 42)
    u = ULID(ulid_obj)
    assert u.timestamp == 1
    assert u.random == 42


def test_ulid_invalid_type():
    with pytest.raises(Exception):
        ULID(123)


def test_ulid_generator_next_and_repr(mocker):
    mock_ulid = make_ulid(777, 999)
    mock_new = mocker.patch("smartutils.ID.gens.ulid.ulid.new", return_value=mock_ulid)
    mock_new.return_value = mock_ulid
    gen = ULIDGenerator()
    next_ulid = next(gen)
    # 26字符
    assert isinstance(next_ulid, str) and len(next_ulid) == 26
    v2 = gen.next_ulid()  # type: ignore
    assert isinstance(v2, LibULID)
    assert gen.__repr__() == "<ULIDGenerator()>"
