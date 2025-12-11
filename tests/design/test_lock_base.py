import asyncio

from smartutils.design.lock.base import AsyncioLock, ProcessLock, ThreadLock, _check


def test_check_all_branches():
    # 非阻塞 timeout>0, warning + False,None
    b, t = _check(False, 5)
    assert b is False and t is None

    # 非阻塞 timeout<=0
    b, t = _check(False, None)
    assert b is False and t is None
    b, t = _check(False, 0)
    assert b is False and t is None

    # 阻塞 timeout=None
    b, t = _check(True, None)
    assert b is True and t is None

    # 阻塞 timeout<0，归为None
    b, t = _check(True, -3)
    assert b is True and t is None

    # 阻塞 timeout>0
    b, t = _check(True, 2)
    assert b is True and t == 2

    # 阻塞 timeout=0, warning + False,None
    b, t = _check(True, 0)
    assert b is False and t is None


async def test_thread_lock_basic():
    lock = ThreadLock()
    assert await lock.acquire()
    assert await lock.locked() is True
    lock.release()
    assert await lock.locked() is False

    # with 语法
    async with lock:
        assert await lock.locked() is True
    assert await lock.locked() is False

    # 非阻塞立即返回
    assert await lock.acquire(blocking=False)
    lock.release()


async def test_process_lock_basic():
    lock = ProcessLock()
    assert await lock.acquire()
    assert await lock.locked() is True
    lock.release()
    assert await lock.locked() is False

    async with lock:
        assert await lock.locked() is True
    assert await lock.locked() is False

    # 非阻塞立即返回
    assert await lock.acquire(blocking=False)
    lock.release()


async def test_thread_lock_timeout():
    lock = ThreadLock()
    assert await lock.acquire()
    # 第二次 acquire 阻塞 0.1s 超时
    assert not await lock.acquire(timeout=0.01)
    lock.release()


async def test_process_lock_timeout():
    lock = ProcessLock()
    assert await lock.acquire()
    assert not await lock.acquire(timeout=0.01)
    lock.release()


async def test_asyncio_lock_basic():
    lock = AsyncioLock()
    acquired = await lock.acquire()
    assert acquired is True
    assert lock.locked()
    lock.release()
    assert not lock.locked()

    # async with
    async with lock:
        assert lock.locked()
    assert not lock.locked()

    # timeout=0 立即返回 False，不加锁
    result = await lock.acquire(timeout=0)
    assert result is False
    assert not lock.locked()

    # timeout>0 加锁后其他协程应等待
    await lock.acquire()
    try:
        # 预计这0.01秒别的协程拿不到锁
        coro = asyncio.create_task(lock.acquire(timeout=0.01))
        await asyncio.sleep(0.02)
        assert not coro.result()
    finally:
        lock.release()


async def test_asyncio_lock_timeout():
    lock = AsyncioLock()
    await lock.acquire()
    # 0.01秒内肯定获取不到锁
    res = await lock.acquire(timeout=0.01)
    assert res is False
    lock.release()

    # acquire后立即release，能抢到
    res = await lock.acquire(timeout=1)
    assert res is True
    lock.release()
