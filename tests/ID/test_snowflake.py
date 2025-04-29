import pytest
from smartutils.ID import Snowflake, SnowflakeGenerator, MAX_INSTANCE, MAX_SEQ


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
    # 反解析
    sf2 = Snowflake.parse(val, epoch=0)
    assert sf2.timestamp == sf.timestamp
    assert sf2.instance == sf.instance
    assert sf2.seq == sf.seq


def test_invalid_instance():
    """测试非法机器ID、序列号、时间戳等参数校验"""
    with pytest.raises(ValueError):
        SnowflakeGenerator(instance=-1)
    with pytest.raises(ValueError):
        SnowflakeGenerator(instance=MAX_INSTANCE + 1)
    with pytest.raises(ValueError):
        Snowflake(timestamp=0, instance=-1)
    with pytest.raises(ValueError):
        Snowflake(timestamp=0, instance=MAX_INSTANCE + 1)
    with pytest.raises(ValueError):
        Snowflake(timestamp=0, instance=1, seq=-1)
    with pytest.raises(ValueError):
        Snowflake(timestamp=0, instance=1, seq=MAX_SEQ + 1)


def test_monotonic_seq():
    """测试同一毫秒内序列号自增"""
    gen = SnowflakeGenerator(instance=1, epoch=0)
    ids = [gen() for _ in range(5)]
    # 低12位应该递增
    seqs = [i & 0xfff for i in ids]
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
    # 检查时间戳是否正确
    assert abs(dt.timestamp() - ((now_epoch + 1000) / 1000)) < 1
