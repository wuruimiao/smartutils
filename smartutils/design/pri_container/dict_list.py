import bisect
from multiprocessing.managers import DictProxy, ListProxy, SyncManager
from typing import Container, Dict, Iterable, Iterator, List, Optional, Sized, Union

from smartutils.design._class import MyBase
from smartutils.design.abstract._sync import AbstractClosable, ClosableProtocol
from smartutils.design.abstract.common import QueueContainerProtocol, RemovableProtocol
from smartutils.design.pri_container.abstract import (
    InstPri,
    PriContainerItemBase,
    PriContainerProtocol,
    TPriContainerItem,
)
from smartutils.log import logger


class PriContainerDictList(
    MyBase,
    AbstractClosable,
    ClosableProtocol,
    Sized,
    Container,
    Iterable[TPriContainerItem],
    QueueContainerProtocol[TPriContainerItem],
    PriContainerProtocol[TPriContainerItem],
    RemovableProtocol[TPriContainerItem],
):
    def __init__(self, manager: Optional[SyncManager] = None):
        # 升序排序
        self._idles: Union[Dict[str, TPriContainerItem], DictProxy]
        self._usings: Union[Dict[str, TPriContainerItem], DictProxy]
        self._idles_sort: Union[List[InstPri], ListProxy]

        self._manager = manager

        if manager is not None:
            # 使用manager生成可进程间共享的dict和list
            self._idles = manager.dict()
            self._usings = manager.dict()
            self._idles_sort = manager.list()
        else:
            self._idles = {}
            self._usings = {}
            self._idles_sort = []

        super().__init__()

    def put(self, item: TPriContainerItem) -> None:
        self.raise_for_closed()
        # 重复释放
        if item.inst_id in self._idles:
            logger.error("{name} exist {item} in idles.", name=self.name, item=item)
            return

        # 释放回来
        if item.inst_id in self._usings:
            self._usings.pop(item.inst_id)

        item.before_put()
        self._idles[item.inst_id] = item

        bisect.insort(
            self._idles_sort,
            InstPri(priority=item.priority, inst_id=item.inst_id),
            key=lambda x: x.priority,
        )  # 必须升序

    def get(self) -> Optional[TPriContainerItem]:
        return self.get_max()

    def _get_end(self, from_min: bool) -> Optional[TPriContainerItem]:
        self.raise_for_closed()
        if not self._idles:
            return None

        inst_pri = self._idles_sort.pop(0 if from_min else -1)
        item = self._idles.pop(inst_pri.inst_id)
        self._usings[item.inst_id] = item
        return item

    def get_min(self) -> Optional[TPriContainerItem]:
        return self._get_end(True)

    def get_max(self) -> Optional[TPriContainerItem]:
        return self._get_end(False)

    def remove(self, item: TPriContainerItem) -> Optional[TPriContainerItem]:
        self.raise_for_closed()

        if item.inst_id in self._usings:
            logger.error("{name} {item} in using, ignore.", name=self.name, item=item)
            return None

        if item.inst_id in self._idles:
            i = None
            for i, inst_pri in enumerate(self._idles_sort):
                if inst_pri.inst_id == item.inst_id:
                    break
            if i is not None:
                self._idles_sort.pop(i)

            return self._idles.pop(item.inst_id)

        return None

    def close(self):
        super().close()
        self._idles.clear()
        self._usings.clear()
        self._manager = None

    def __len__(self) -> int:
        return len(self._usings) + len(self._idles)

    def __contains__(self, x: object) -> bool:
        if not isinstance(x, PriContainerItemBase):
            return False
        return x.inst_id in self._usings or x.inst_id in self._idles

    def __iter__(self) -> Iterator[TPriContainerItem]:
        for item in self._idles.values():
            yield item
        for item in self._usings.values():
            yield item

    def empty(self) -> bool:
        return len(self) == 0

    def full(self) -> bool:
        return False
