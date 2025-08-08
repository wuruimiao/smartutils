import bisect
from multiprocessing.managers import DictProxy, ListProxy, SyncManager
from typing import Container, Dict, Iterable, Iterator, List, Optional, Sized, Union

from smartutils.design._class import MyBase
from smartutils.design.abstract._sync import (
    AbstractClosable,
    ClosableProtocol,
    QueueContainerProtocol,
)
from smartutils.design.abstract.common import RemovableProtocol
from smartutils.design.pri_container.abstract import (
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
    Iterable,
    QueueContainerProtocol[TPriContainerItem],
    PriContainerProtocol[TPriContainerItem],
    RemovableProtocol[TPriContainerItem],
):
    def __init__(self, manager: Optional[SyncManager] = None):
        # 升序排序
        self._idles: Union[List[TPriContainerItem], ListProxy]
        self._usings: Union[Dict[TPriContainerItem, bool], DictProxy]

        self._manager = manager

        if manager is not None:
            # 使用manager生成可进程间共享的dict和list
            self._idles = manager.list()
            self._usings = manager.dict()
        else:
            self._idles = []
            self._usings = {}

        super().__init__()

    def put(self, item: TPriContainerItem) -> None:
        self.raise_for_closed()
        if item in self._usings:
            self._usings.pop(item)
        item.before_put()
        bisect.insort(self._idles, item)  # 必须升序

    def _get_end(self, from_min: bool) -> Optional[TPriContainerItem]:
        self.raise_for_closed()
        item = self._idles.pop(0 if from_min else -1)
        self._usings[item] = True
        return item

    def get_min(self) -> Optional[TPriContainerItem]:
        return self._get_end(True)

    def get_max(self) -> Optional[TPriContainerItem]:
        return self._get_end(False)

    def remove(self, item: TPriContainerItem) -> Optional[TPriContainerItem]:
        self.raise_for_closed()
        if item in self._usings:
            logger.error(
                "{name} {item} in using, do nothing.", name=self.name, item=item
            )
            return None
        i = None

        for i, _item in enumerate(self._idles):
            if _item == item:
                break
        if i is not None:
            return self._idles.pop(i)
        return None

    def close(self):
        super().close()
        self._idles.clear()
        self._usings.clear()
        self._manager = None

    def __len__(self) -> int:
        return len(self._usings) + len(self._idles)

    def __contains__(self, x: object) -> bool:
        return x in self._usings or x in self._idles

    def __iter__(self) -> Iterator[TPriContainerItem]:
        for item in self._idles:
            yield item
        for item in self._usings:
            yield item

    def get(self) -> Optional[TPriContainerItem]:
        return self.get_max()

    def empty(self) -> bool:
        return len(self) == 0

    def full(self) -> bool:
        return False
