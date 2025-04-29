import asyncio
import re
import time

import pytest

from smartutils.log import logger
from smartutils.timer import Timer, timeit


def test_timer_basic(monkeypatch):
    cg = iter([0.0, 1.0, 2.0, 3.0, 4.0])

    def fake_counter():
        return next(cg)

    t = Timer(func=fake_counter)
    assert not t.running
    assert t.elapsed == 0.0

    t.start()  # fake_counter() -> 0.0
    assert t.running
    assert t.elapsed == 1.0  # fake_counter() -> 1.0, 1.0 - 0.0 = 1.0 正在运行时
    with pytest.raises(RuntimeError):
        t.start()

    t.stop()  # fake_counter() -> 2.0, 2.0 - 0.0 = 2.0
    assert not t.running
    assert t.elapsed == 2.0  # 累计时间


def test_timer_with_context():
    t = Timer()
    with t:
        time.sleep(0.01)
    assert t.elapsed >= 0.01
    # 可以再次用
    t.reset()
    with t:
        time.sleep(0.01)
    assert t.elapsed >= 0.01


async def test_timer_async_with_context():
    t = Timer()
    async with t:
        await asyncio.sleep(0.01)
    assert t.elapsed >= 0.01
    # 可以重复使用
    t.reset()
    async with t:
        await asyncio.sleep(0.005)
    assert t.elapsed >= 0.005


def test_timer_elapsed_during_running(monkeypatch):
    # 测试 running 时 elapsed 随时间变化
    fake_time = [0]

    def fake_counter():
        return fake_time[0]

    t = Timer(func=fake_counter)
    t.start()
    fake_time[0] = 2
    assert 1.9 < t.elapsed < 2.1
    t.stop()
    assert 1.9 < t.elapsed < 2.1


def test_timer_running_property():
    t = Timer()
    assert not t.running
    t.start()
    assert t.running
    t.stop()
    assert not t.running


def test_timer_multiple_intervals():
    t = Timer()
    t.start()
    time.sleep(0.002)
    t.stop()
    first = t.elapsed
    t.start()
    time.sleep(0.002)
    t.stop()
    second = t.elapsed - first
    assert first > 0
    assert second > 0
    assert t.elapsed > first


@pytest.fixture
def capture_logger(monkeypatch):
    logs = []
    monkeypatch.setattr(logger, "debug", lambda msg: logs.append(msg))
    return logs


def test_timeit_sync(capture_logger):
    @timeit("TestSync: ")
    def foo(x):
        time.sleep(0.02)
        return x * 2

    result = foo(3)
    assert result == 6
    # 检查 logger 是否被调用，内容是否包含函数名和秒数
    assert any("TestSync: foo cost" in msg for msg in capture_logger)
    # 检查耗时格式
    assert re.search(r"TestSync: foo cost [\d\.]+s", capture_logger[0])


async def test_timeit_async(capture_logger):
    @timeit("TestAsync: ")
    async def bar(x):
        await asyncio.sleep(0.02)
        return x + 1

    result = await bar(7)
    assert result == 8
    assert any("TestAsync: bar cost" in msg and "(async)" in msg for msg in capture_logger)
    # 检查耗时格式
    assert re.search(r"TestAsync: bar cost [\d\.]+s \(async\)", capture_logger[0])


def test_timeit_return_value(capture_logger):
    @timeit()
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert "add cost" in capture_logger[0]


async def test_timeit_async_accuracy(capture_logger):
    @timeit()
    async def sleep_func():
        await asyncio.sleep(0.03)
        return 1

    await sleep_func()
    # 检查输出的时间大于0.025s
    m = re.search(r"cost ([\d\.]+)s", capture_logger[0])
    assert m is not None
    assert float(m.group(1)) >= 0.025


def test_timeit_no_prefix(capture_logger):
    @timeit()
    def nothing():
        return "ok"

    assert nothing() == "ok"
    assert "nothing cost" in capture_logger[0]


def test_stop_without_start_raises():
    t = Timer()
    # 直接stop，不先start，应抛出RuntimeError
    import pytest
    with pytest.raises(RuntimeError, match="Timer not started"):
        t.stop()
