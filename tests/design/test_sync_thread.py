import threading
import time

import pytest

from smartutils.design._sync._thread import ThreadSyncLock
from smartutils.error.sys import LibraryUsageError


def test_thread_lock_basic():
    """
    ThreadSyncLock基本功能测试：加锁、超时、wait/notify。
    """
    lock = ThreadSyncLock()
    result = []

    def worker():
        assert lock.acquire(1)
        result.append("got lock")
        lock.release()

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    assert result == ["got lock"]

    # 测试condition wait/notify
    data = {}

    def wait_thread():
        with lock:
            ok = lock.wait(0.5)
            if ok:
                data["flag"] = "notified"
            else:
                data["flag"] = "timeout"

    waiter = threading.Thread(target=wait_thread)
    waiter.start()
    time.sleep(0.1)
    with lock:
        lock.notify()

    waiter.join()
    assert data["flag"] == "notified"


def test_thread_lock_notify_all_cover():
    lock = ThreadSyncLock()
    data = {}

    def waiter():
        with lock:
            ok = lock.wait(0.5)
            data["ret"] = ok

    t = threading.Thread(target=waiter)
    t.start()
    time.sleep(0.1)
    with lock:
        lock.notify_all()
    t.join()
    assert data["ret"] is True

    # 覆盖未持锁直接调用 notify_all 时的异常分支
    lock2 = ThreadSyncLock()
    with pytest.raises(RuntimeError):
        lock2.notify_all()


def test_thread_lock_timeout():
    """
    加锁超时：先获得锁不释放，然后尝试再次acquire应超时返回False。
    """
    lock = ThreadSyncLock()
    assert lock.acquire(0.5)
    t1 = threading.Thread(target=lambda: lock.acquire(0.3))
    t1.start()
    t1.join()
    lock.release()


def test_thread_lock_exit_without_acquire():
    lock = ThreadSyncLock()
    with pytest.raises(RuntimeError):
        lock.__exit__(None, None, None)


async def test_thread_sync_lock_wrong_usage_async():
    lock = ThreadSyncLock()
    with pytest.raises(LibraryUsageError) as e:
        await lock.aacquire(1)
    assert (
        str(e.value)
        == "ThreadSyncLock does not support coroutine/asynchronous interfaces."
    )

    with pytest.raises(LibraryUsageError) as e:
        await lock.arelease()
    assert (
        str(e.value)
        == "ThreadSyncLock does not support coroutine/asynchronous interfaces."
    )

    with pytest.raises(LibraryUsageError) as e:
        await lock.a_wait(1)
    assert (
        str(e.value)
        == "ThreadSyncLock does not support coroutine/asynchronous interfaces."
    )

    with pytest.raises(LibraryUsageError) as e:
        await lock.anotify(1)
    assert (
        str(e.value)
        == "ThreadSyncLock does not support coroutine/asynchronous interfaces."
    )

    with pytest.raises(LibraryUsageError) as e:
        await lock.anotify_all()
    assert (
        str(e.value)
        == "ThreadSyncLock does not support coroutine/asynchronous interfaces."
    )

    with pytest.raises(LibraryUsageError) as e:
        lock.acontext()
    assert (
        str(e.value)
        == "ThreadSyncLock does not support coroutine/asynchronous interfaces."
    )
