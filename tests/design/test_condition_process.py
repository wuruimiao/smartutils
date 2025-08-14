import multiprocessing
import time

import pytest

from smartutils.design.condition._process import ProcessCondition


def test_process_lock_basic():
    """
    ProcessSyncLock多进程功能测试。
    """
    manager = multiprocessing.Manager()
    lock = ProcessCondition(manager=manager)

    def child(queue):
        ok = lock.acquire(timeout=1)
        if ok:
            queue.put("child-lock")
            time.sleep(1)  # hold the lock a bit
            lock.release()

    result_q = multiprocessing.Queue()
    p = multiprocessing.Process(target=child, args=(result_q,))
    p.start()
    # 等待子进程持锁，然后主进程尝试acquire，会等待
    time.sleep(0.1)
    got = lock.acquire(timeout=0.5)
    assert not got  # 应超时
    # 释放
    p.join()
    # 再次acquire应能拿到
    assert lock.acquire(timeout=1)
    lock.release()
    assert result_q.get() == "child-lock"


def test_process_lock_notify():
    """
    多进程条件变量wait/notify。
    """
    manager = multiprocessing.Manager()
    lock = ProcessCondition(manager=manager)
    result_q = multiprocessing.Queue()

    def waiter_task(q):
        with lock:
            ok = lock.wait(timeout=0.5)
            q.put(ok)

    waiter = multiprocessing.Process(target=waiter_task, args=(result_q,))
    waiter.start()
    time.sleep(0.1)
    with lock:
        lock.notify()
    waiter.join()
    assert result_q.get() is True


def test_process_lock_notify_all_cover():
    """
    覆盖 ProcessSyncLock.notify_all 的正常路径和错误分支。
    """
    manager = multiprocessing.Manager()
    lock = ProcessCondition(manager=manager)
    result_q = multiprocessing.Queue()

    def waiter_task(q):
        with lock:
            ok = lock.wait(timeout=0.5)
            q.put(ok)

    # 一次性唤醒所有等待者
    waiters = [
        multiprocessing.Process(target=waiter_task, args=(result_q,)) for _ in range(2)
    ]
    for w in waiters:
        w.start()

    with lock:
        # 多进程环境下，wait的测试无法统计，在这里覆盖下
        assert not lock.wait(timeout=0.1)
        lock.notify_all()
    for w in waiters:
        w.join()
    result = [result_q.get() for _ in range(2)]
    assert all(result)

    # ——异常分支：未持锁直接调用notify_all应抛错（标准库实现为RuntimeError）
    lock2 = ProcessCondition(manager=manager)
    with pytest.raises(RuntimeError):
        lock2.notify_all()


def test_process_lock_exit_shutdown_cover():
    """
    覆盖ProcessSyncLock自带Manager情况下__exit__分支，即资源回收分支。
    """
    # 不指定manager,让内部自动创建与关闭
    lock = ProcessCondition()
    # 模拟 with 执行完关闭
    lock.acquire(timeout=0.1)
    lock.__exit__(None, None, None)


async def test_thread_async_with():
    lock = ProcessCondition()
    async with lock:
        lock.acquire()
