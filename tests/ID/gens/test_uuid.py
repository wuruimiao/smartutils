import uuid

import pytest

from smartutils.ID.gens.uuid import UUIDGenerator


def test_uuid_generator_next_and_type():
    gen = UUIDGenerator()
    u_str = next(gen)
    assert isinstance(u_str, str)
    assert len(u_str) == 36
    u_obj = uuid.UUID(u_str)
    assert isinstance(u_obj, uuid.UUID)


def test_uuid_generator_next_uuid():
    u_obj = UUIDGenerator.next_uuid()
    assert isinstance(u_obj, uuid.UUID)
    # 字符串格式
    assert len(str(u_obj)) == 36
    # 再次调用不会重复
    assert UUIDGenerator.next_uuid() != u_obj


def test_uuid_generator_repr():
    gen = UUIDGenerator()
    assert gen.__repr__() == "<UUIDGenerator()>"


# 唯一性简单测试
def test_uuid_unique_multiple():
    gen = UUIDGenerator()
    uuids = {next(gen) for _ in range(10)}
    assert len(uuids) == 10
