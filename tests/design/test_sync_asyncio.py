import asyncio

import pytest

from smartutils.design._sync._async import AsyncioSyncLock
from smartutils.error.sys import LibraryUsageError


async def test_asyncio_lock_basic():
    """
    AsyncioSyncLock基本加锁/超时/condition测试。
    """
    lock = AsyncioSyncLock()
    assert await lock.aacquire(1)
    await lock.arelease()

    result = {}

    async def waiter():
        async with lock.acontext():
            ret = await lock.a_wait(0.5)
            result["got"] = ret

    w = asyncio.create_task(waiter())
    await asyncio.sleep(0.1)
    async with lock.acontext():
        await lock.anotify()
    await w
    assert result["got"] is True


async def test_asyncio_a_wait_timeout():
    """
    AsyncioSyncLock：wait超时分支。
    """
    lock = AsyncioSyncLock()
    async with lock.acontext():
        ok = await lock.a_wait(0.01)
        assert ok is False


async def test_asyncio_acquire_timeout():
    """
    AsyncioSyncLock：wait超时分支。
    """
    lock = AsyncioSyncLock()
    async with lock.acontext():
        ok = await lock.aacquire(0.01)
        assert ok is False


async def test_asyncio_lock_notify_and_notify_all_cover():
    lock = AsyncioSyncLock()
    # notify/notify_all 在未持有锁时会引发RuntimeError
    with pytest.raises(RuntimeError):
        await lock.anotify()
    with pytest.raises(RuntimeError):
        await lock.anotify_all()


async def test_asyncio_lock_acontext_finally_cover():
    lock = AsyncioSyncLock()

    class MyError(Exception):
        pass

    with pytest.raises(MyError):
        async with lock.acontext():
            raise MyError("cover finally branch")


async def test_asyncio_sync_lock_wrong_usage_sync():
    lock = AsyncioSyncLock()
    with pytest.raises(LibraryUsageError) as e:
        lock.acquire(1)
    assert (
        str(e.value) == "Only asynchronous interface is supported, please use aacquire."
    )

    with pytest.raises(LibraryUsageError) as e:
        lock.release()
    assert (
        str(e.value) == "Only asynchronous interface is supported, please use arelease."
    )

    with pytest.raises(LibraryUsageError) as e:
        lock.wait(1)
    assert (
        str(e.value) == "Only asynchronous interface is supported, please use a_wait."
    )

    with pytest.raises(LibraryUsageError) as e:
        lock.notify(1)
    assert (
        str(e.value) == "Only asynchronous interface is supported, please use anotify."
    )

    with pytest.raises(LibraryUsageError) as e:
        lock.notify_all()
    assert (
        str(e.value)
        == "Only asynchronous interface is supported, please use anotify_all."
    )

    with pytest.raises(LibraryUsageError) as e:
        with lock:
            pass
    assert str(e.value) == "Please use 'async with' in asyncio environment."

    with pytest.raises(LibraryUsageError) as e:
        lock.__exit__(None, None, None)
    assert str(e.value) == "Please use 'async with' in asyncio environment."
