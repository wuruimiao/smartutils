from __future__ import annotations

import threading
from typing import Union

from smartutils.design._lock.abstract import ConditionProtocol


class ThreadCondition(ConditionProtocol):
    """
    线程环境专用的同步锁与条件变量实现。

    - 适合多线程环境；底层基于 threading.Condition，支持加锁、解锁、条件等待与唤醒。
    - 不支持异步/协程接口，调用相关 async 方法会抛出 NotImplementedError。
    - 遵循 ISyncLock 抽象接口，实现开闭原则。
    - 推荐配合 with 使用上下文自动加解锁。
    """

    def __init__(self, *, timeout: Union[float, int] = 60 * 60 * 1) -> None:
        """
        初始化线程同步锁。
        """
        self._cond = threading.Condition()
        self._timeout = timeout

    def acquire(self, timeout: float | int) -> bool:
        """
        获取锁，超时会阻塞至 timeout 秒：
        若期间获得锁返回 True，否则 False。
        """
        return self._cond.acquire(timeout=timeout)

    def release(self) -> None:
        """
        释放锁。
        """
        self._cond.release()

    def wait(self, timeout: float | int) -> bool:
        """
        条件等待：必须先获得锁。超时或被其他线程 notify 唤醒。
        返回：被唤醒 True，超时 False。
        """
        return self._cond.wait(timeout=timeout)

    def notify(self, n: int = 1) -> None:
        """
        唤醒当前条件队列中最多 n 个线程。
        """
        self._cond.notify(n)

    def notify_all(self) -> None:
        """
        唤醒所有处于条件等待的线程。
        """
        self._cond.notify_all()

    def __enter__(self) -> ThreadCondition:
        self.acquire(timeout=self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()
