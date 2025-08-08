from __future__ import annotations

from smartutils.design.pri_container.abstract import PriContainerItemBase
from smartutils.design.pri_container.dict_list import PriContainerDictList
from smartutils.time import get_now_stamp_float


class PriTSItem(PriContainerItemBase):
    def before_put(self):
        self._priority = get_now_stamp_float()

    def after_get(self): ...


class PriTSContainerDictList(PriContainerDictList[PriTSItem]): ...


class PriUseNoItem(PriContainerItemBase):
    def before_put(self): ...

    def after_get(self):
        self._priority += 1


class PriUseNoContainerDictList(PriContainerDictList[PriUseNoItem]): ...
