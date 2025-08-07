import asyncio
import time

import pytest

from smartutils.design.condition._async import AsyncioCondition
from smartutils.design.condition_container.base import AsyncConditionContainer
from smartutils.design.container.pri_timestamp import PriTSContainerDictList


@pytest.fixture
def cond_container():
    return AsyncConditionContainer(
        container=PriTSContainerDictList(), condition=AsyncioCondition()
    )


async def test_async_cond_container_put_and_get(cond_container):
    # put 应成功, get 应返回相同值
    assert await cond_container.put("hello1", timeout=1) is True
    assert await cond_container.put("hello2", timeout=1) is True
    assert await cond_container.get(timeout=1) == "hello2"
    assert await cond_container.get(timeout=1, block=False) == "hello1"
    # 取空，再get应返回None
    assert await cond_container.get(timeout=1, block=False) is None
    assert cond_container.empty()


async def test_async_cond_container_put_multitask(cond_container):
    """
    协程环境下，生产者消费者
    """
    results = []

    async def producer():
        for i in range(3):
            assert await cond_container.put(f"item{i}", timeout=1)
            # 为了模拟真实并发，可适当加一点延迟
            await asyncio.sleep(0.01)

    async def consumer():
        for _ in range(3):
            v = await cond_container.get(timeout=1)
            results.append(v)
            await asyncio.sleep(0.01)

    await asyncio.gather(producer(), consumer())
    assert set(results) == {"item0", "item1", "item2"}


async def test_async_cond_container_timeout(cond_container):
    # 空容器 get 超时
    t0 = time.time()
    assert await cond_container.get(timeout=0.2) is None
    assert 0.15 < (time.time() - t0) < 1


async def test_async_cond_container_notify_on_put(cond_container):
    """
    等效于“put通知 consumer 消费”
    """
    results = []

    async def consumer():
        v = await cond_container.get(timeout=1)
        results.append(v)

    consumer_task = asyncio.create_task(consumer())
    await asyncio.sleep(0.1)  # 保证 consumer 已进入等待
    await cond_container.put("wakeup", timeout=1)
    await consumer_task
    assert results == ["wakeup"]


async def test_async_cond_container_acquire_timeout(cond_container):
    """
    测试协程环境下获取锁超时
    """
    # 通过锁资源实现
    cond = cond_container._cond

    async def locker():
        got = await cond.acquire(timeout=1)
        assert got
        await asyncio.sleep(1.0)  # 持有锁达到 1 秒
        cond.release()

    locker_task = asyncio.create_task(locker())
    await asyncio.sleep(0.05)  # 确保 locker 已持有锁

    start = time.time()
    res = await cond_container.get(timeout=0.2)
    end = time.time()
    await locker_task

    assert res is None
    assert 0.18 < (end - start) < 0.5  # 等待时间近于 0.2s


async def test_async_cond_container_put_timeout_false(cond_container):
    """
    测试 put 超时返回 False
    """
    cond = cond_container._cond

    async def locker():
        got = await cond.acquire(timeout=1)
        assert got
        await asyncio.sleep(1.0)
        cond.release()

    locker_task = asyncio.create_task(locker())
    await asyncio.sleep(0.05)

    start = time.time()
    res = await cond_container.put(1, timeout=0.2)
    end = time.time()
    await locker_task

    assert res is False
    assert 0.18 < (end - start) < 0.5


def test_async_cond_container_getattr(cond_container):
    cond_container.push("a", 1)
    cond_container.push("b", 2)
    cond_container.push("c", 3)
    assert cond_container.pop_max() == "c"
    assert cond_container.pop_min() == "a"

    with pytest.raises(TypeError) as e:
        assert len(cond_container) == 1
    assert str(e.value) == "object of type 'AsyncConditionContainer' has no len()"
    with pytest.raises(TypeError) as e:
        assert "b" in cond_container
    assert str(e.value) == "argument of type 'AsyncConditionContainer' is not iterable"
