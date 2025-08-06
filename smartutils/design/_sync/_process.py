from __future__ import annotations

from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from multiprocessing.synchronize import Condition
from typing import Optional, Union

from smartutils.design._sync.abstract import ILock


class ProcessSyncLock(ILock):
    """
    适用于多进程环境的同步锁/条件变量实现，基于 multiprocessing.Manager.Condition。
    线程和进程安全。支持互斥锁、阻塞条件等待和唤醒。

    注意事项：
    ----------
    1. 只实现同步接口（acquire/release/wait/notify/notify_all 等），异步接口不支持，调用会抛 NotImplementedError。
    2. 应在同一 manager 域下多进程共享本对象，否则将无法跨进程同步。
    3. timeout 参数为必填，单位秒，float/int 皆可。超时返回 False，成功返回 True。
    4. 不支持 async with 等异步接口。
    """

    def __init__(
        self,
        *,
        manager: Optional[SyncManager] = None,
        timeout: Union[float, int] = 60 * 60 * 1,
    ):
        """
        初始化多进程锁。可外部注入一个 Manager 或自动创建一个新 Manager。
        """
        if manager is None:
            manager = Manager()
            self._manager_owner = True
        else:
            self._manager_owner = False
        self._condition: Condition = manager.Condition()  # type: ignore
        self._manager = manager
        self._timeout = timeout

    def acquire(self, timeout: float | int) -> bool:
        """
        获取进程间锁，超时自动返回。
        """
        return self._condition.acquire(timeout=timeout)

    def release(self) -> None:
        """
        释放进程间锁。
        """
        self._condition.release()

    def wait(self, timeout: float | int) -> bool:
        """
        条件等待，超时返回 False，被 notify/notify_all 唤醒返回 True。
        需已持有锁。
        """
        return self._condition.wait(timeout=timeout)

    def notify(self, n: int = 1) -> None:
        """
        唤醒最多 n 个等待进程。
        """
        self._condition.notify(n)

    def notify_all(self) -> None:
        """
        唤醒所有等待进程。
        """
        self._condition.notify_all()

    def __enter__(self) -> ProcessSyncLock:
        self.acquire(timeout=self._timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        # 若本类创建了 Manager，自动关闭资源
        if self._manager_owner:
            self._manager.shutdown()
