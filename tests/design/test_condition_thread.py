import threading
import time

import pytest

from smartutils.design.condition._thread import ThreadCondition


def test_thread_lock_basic():
    """
    ThreadSyncLock基本功能测试：加锁、超时、wait/notify。
    """
    lock = ThreadCondition()
    result = []

    def worker():
        assert lock.acquire(timeout=1)
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
            ok = lock.wait(timeout=0.5)
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
    lock = ThreadCondition()
    data = {}

    def waiter():
        with lock:
            ok = lock.wait(timeout=0.5)
            data["ret"] = ok

    t = threading.Thread(target=waiter)
    t.start()
    time.sleep(0.1)
    with lock:
        lock.notify_all()
    t.join()
    assert data["ret"] is True

    # 覆盖未持锁直接调用 notify_all 时的异常分支
    lock2 = ThreadCondition()
    with pytest.raises(RuntimeError):
        lock2.notify_all()


def test_thread_lock_timeout():
    """
    加锁超时：先获得锁不释放，然后尝试再次acquire应超时返回False。
    """
    lock = ThreadCondition()
    assert lock.acquire(timeout=0.5)
    t1 = threading.Thread(target=lambda: lock.acquire(timeout=0.3))
    t1.start()
    t1.join()
    lock.release()


def test_thread_lock_exit_without_acquire():
    lock = ThreadCondition()
    with pytest.raises(RuntimeError):
        lock.__exit__(None, None, None)
