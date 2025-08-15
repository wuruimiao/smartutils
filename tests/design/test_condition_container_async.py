import asyncio
import time
from typing import Iterator, Optional

import pytest

from smartutils.design.abstract.common import QueueContainerIterableProtocol
from smartutils.design.condition._async import AsyncioCondition
from smartutils.design.condition_container.base import AsyncConditionContainer


class TmpContainer(QueueContainerIterableProtocol[str]):
    def __init__(self) -> None:
        self._list = []
        self._limit = 3
        super().__init__()

    def __iter__(self) -> Iterator[str]:
        return iter(self._list)

    def put(self, item: str) -> None:
        self._list.append(item)

    def get(self) -> Optional[str]:
        return self._list.pop(-1)

    def empty(self) -> bool:
        return not self._list

    def full(self) -> bool:
        return len(self._list) == self._limit


@pytest.fixture
def cond_container():
    return AsyncConditionContainer(
        container=TmpContainer(), condition=AsyncioCondition()
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
