import threading
import time
from typing import Optional

import pytest

from smartutils.design.abstract.common import (
    QueueContainerProtocol,
)
from smartutils.design.condition._thread import ThreadCondition
from smartutils.design.condition_container.base import ConditionContainer


class TmpContainer(QueueContainerProtocol[str]):
    def __init__(self) -> None:
        self._list = []
        self._limit = 3
        super().__init__()

    def put(self, item: str) -> None:
        self._list.append(item)

    def get(self) -> Optional[str]:
        return self._list.pop(-1)

    def empty(self) -> bool:
        return not self._list

    def full(self) -> bool:
        return self.qsize() >= self._limit

    def qsize(self) -> int:
        return len(self._list)


@pytest.fixture
def cond_container():
    return ConditionContainer(container=TmpContainer(), condition=ThreadCondition())


def test_put_and_get(cond_container):
    # put 应成功, get 应返回相同值
    assert cond_container.put("hello1", timeout=1) is True
    assert cond_container.put("hello2", timeout=1) is True
    assert cond_container.full()
    assert cond_container.get(timeout=1) == "hello2"
    assert cond_container.get(timeout=1, block=False) == "hello1"
    # 取空，再get应返回None
    assert cond_container.get(timeout=1, block=False) is None
    assert cond_container.empty()


def test_put_multithread(cond_container):
    import threading

    results = []

    def producer():
        for i in range(3):
            assert cond_container.put(f"item{i}", timeout=1)

    def consumer():
        for _ in range(3):
            v = cond_container.get(timeout=1)
            results.append(v)

    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert set(results) == {"item0", "item1", "item2"}


def test_timeout(cond_container):
    # 空容器 get 超时
    t0 = time.time()
    assert cond_container.get(timeout=0.2) is None
    assert 0.15 < (time.time() - t0) < 1


def test_notify_on_put(cond_container):
    # 多线程下 put 通知后续 consumer
    results = []

    def consumer():
        v = cond_container.get(timeout=1)
        results.append(v)

    t = threading.Thread(target=consumer)
    t.start()
    # 保证consumer先进入等待
    time.sleep(0.1)
    cond_container.put("wakeup", timeout=1)
    t.join()
    assert results == ["wakeup"]


def test_cond_container_get_none(cond_container):
    # 占用锁线程
    def locker():
        got = cond_container._cond.acquire(timeout=1)
        assert got
        time.sleep(1.0)  # 持有锁达到 1 秒
        cond_container._cond.release()

    t = threading.Thread(target=locker)
    t.start()
    time.sleep(0.05)  # 确保 t 已经持有锁

    # 尝试获取锁，0.2 秒应该会失败
    start = time.time()
    assert cond_container.get(timeout=0.2) is None
    end = time.time()
    t.join()

    assert 0.18 < (end - start) < 0.5  # 确实等了小于 locker 的占用时长


def test_cond_container_put_False(cond_container):
    # 占用锁线程
    def locker():
        got = cond_container._cond.acquire(timeout=1)
        assert got
        time.sleep(1.0)  # 持有锁达到 1 秒
        cond_container._cond.release()

    t = threading.Thread(target=locker)
    t.start()
    time.sleep(0.05)  # 确保 t 已经持有锁

    # 尝试获取锁，0.2 秒应该会失败
    start = time.time()
    assert cond_container.put(1, timeout=0.2) is False
    end = time.time()
    t.join()

    assert 0.18 < (end - start) < 0.5  # 确实等了小于 locker 的占用时长
