import asyncio

import pytest

from smartutils.design.condition._async import AsyncioCondition
from smartutils.error.sys import LibraryUsageError


async def test_asyncio_lock_basic():
    """
    AsyncioSyncLock基本加锁/超时/condition测试。
    """
    lock = AsyncioCondition()
    assert await lock.acquire(timeout=1)
    lock.release()

    result = {}

    async def waiter():
        async with lock:
            ret = await lock.wait(timeout=0.5)
            result["got"] = ret

    w = asyncio.create_task(waiter())
    await asyncio.sleep(0.1)
    async with lock:
        lock.notify()
    await w
    assert result["got"] is True


async def test_asyncio_a_wait_timeout():
    """
    AsyncioSyncLock：wait超时分支。
    """
    lock = AsyncioCondition()
    async with lock:
        ok = await lock.wait(timeout=0.01)
        assert ok is False


async def test_asyncio_acquire_timeout():
    """
    AsyncioSyncLock：wait超时分支。
    """
    lock = AsyncioCondition()
    async with lock:
        ok = await lock.acquire(timeout=0.01)
        assert ok is False


async def test_asyncio_lock_notify_and_notify_all_cover():
    lock = AsyncioCondition()
    # notify/notify_all 在未持有锁时会引发RuntimeError
    with pytest.raises(RuntimeError):
        lock.notify()
    with pytest.raises(RuntimeError):
        lock.notify_all()


async def test_asyncio_lock_acontext_finally_cover():
    lock = AsyncioCondition()

    class MyError(Exception):
        pass

    with pytest.raises(MyError):
        async with lock:
            raise MyError("cover finally branch")


async def test_asyncio_lock_non_block():
    lock = AsyncioCondition()
    assert await lock.acquire(block=False)


async def test_asyncio_lock_wait_non_lock():
    lock = AsyncioCondition()
    assert await lock.acquire()
    with pytest.raises(asyncio.TimeoutError) as e:
        await asyncio.wait_for(lock.wait(), 0.1)
    assert str(e.value) == ""


async def test_asyncio_lock_sync_with():
    lock = AsyncioCondition()
    with pytest.raises(LibraryUsageError) as e:
        with lock:
            ...
    assert str(e.value) == "[AsyncioCondition] does not support sync with"
