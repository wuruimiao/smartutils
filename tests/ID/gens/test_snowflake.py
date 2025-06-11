import time
from datetime import timedelta, timezone

import pytest

from smartutils.error.sys import LibraryUsageError
from smartutils.ID.gens.snowflake import (
    MAX_INSTANCE,
    MAX_SEQ,
    MAX_TS,
    Snowflake,
    SnowflakeClockMovedBackwards,
    SnowflakeGenerator,
    SnowflakeTimestampOverflow,
)


def test_snowflake_parse_and_int():
    """测试 Snowflake 解析和还原"""
    sf = Snowflake(timestamp=12345678, instance=42, epoch=10000, seq=321)
    val = int(sf)
    # 反解析
    sf2 = Snowflake.parse(val, epoch=10000)
    assert sf2.timestamp == 12345678
    assert sf2.instance == 42
    assert sf2.seq == 321
    assert sf2.epoch == 10000
    # value属性一致
    assert sf2.value == val


def test_snowflake_repr_and_properties():
    sf = Snowflake(timestamp=1000, instance=5, epoch=100, seq=10)
    text = repr(sf)
    assert "Snowflake(" in text
    assert sf.timedelta == timedelta(milliseconds=100)
    assert sf.milliseconds == 1000 + 100
    assert abs(sf.seconds - ((1000 + 100) / 1000)) < 1
    dt_utc = sf.datetime
    dt_other = sf.datetime_tz(timezone(timedelta(hours=8)))
    assert dt_utc.tzinfo is not None
    assert dt_other.utcoffset().total_seconds() == 8 * 3600


def test_snowflake_generator_basic():
    """测试 SnowflakeGenerator 生成的ID唯一且递增"""
    gen = SnowflakeGenerator(instance=1, epoch=0)
    prev = gen()
    for _ in range(10):
        cur = gen()
        assert cur > prev
        prev = cur


def test_snowflake_generator_snowflake_obj():
    """测试 SnowflakeGenerator 生成 Snowflake 对象"""
    gen = SnowflakeGenerator(instance=1, epoch=0)
    sf = gen.next_snowflake()
    assert isinstance(sf, Snowflake)
    val = int(sf)
    sf2 = Snowflake.parse(val, epoch=0)
    assert sf2.timestamp == sf.timestamp
    assert sf2.instance == sf.instance
    assert sf2.seq == sf.seq


def test_invalid_instance():
    """测试非法机器ID、序列号、时间戳等参数校验"""
    with pytest.raises(LibraryUsageError):
        SnowflakeGenerator(instance=-1)
    with pytest.raises(LibraryUsageError):
        SnowflakeGenerator(instance=MAX_INSTANCE + 1)
    with pytest.raises(LibraryUsageError):
        Snowflake(timestamp=0, instance=-1)
    with pytest.raises(LibraryUsageError):
        Snowflake(timestamp=0, instance=MAX_INSTANCE + 1)
    with pytest.raises(LibraryUsageError):
        Snowflake(timestamp=0, instance=1, seq=-1)
    with pytest.raises(LibraryUsageError):
        Snowflake(timestamp=0, instance=1, seq=MAX_SEQ + 1)


def test_invalid_generator_timestamp_epoch():
    import time as pyt

    cur = int(pyt.time() * 1000)
    # timestamp < 0
    with pytest.raises(LibraryUsageError):
        SnowflakeGenerator(instance=1, timestamp=-1)
    # epoch < 0
    with pytest.raises(LibraryUsageError):
        SnowflakeGenerator(instance=1, epoch=-1)
    # timestamp > now
    with pytest.raises(LibraryUsageError):
        SnowflakeGenerator(instance=1, timestamp=cur + 10000)
    # epoch > now
    with pytest.raises(LibraryUsageError):
        SnowflakeGenerator(instance=1, epoch=cur + 20000)


def test_snowflake_int_value():
    sf = Snowflake(timestamp=1234, instance=1)
    val = int(sf)
    assert isinstance(val, int)
    assert val == sf.value


def test_monotonic_seq():
    """测试同一毫秒内序列号自增"""
    gen = SnowflakeGenerator(instance=1, epoch=0)
    ids = [gen() for _ in range(5)]
    seqs = [i & 0xFFF for i in ids]
    assert seqs == sorted(seqs)


def test_generator_iter():
    """测试生成器可迭代协议"""
    gen = SnowflakeGenerator(instance=2, epoch=0)
    it = iter(gen)
    ids = [next(it) for _ in range(3)]
    assert len(set(ids)) == 3


def test_snowflake_datetime():
    """测试 Snowflake 的时间属性"""
    now_epoch = 1609459200000  # 2021-01-01 00:00:00
    sf = Snowflake(timestamp=1000, instance=1, epoch=now_epoch)
    dt = sf.datetime
    assert abs(dt.timestamp() - ((now_epoch + 1000) / 1000)) < 1
