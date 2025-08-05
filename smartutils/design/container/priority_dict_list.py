from multiprocessing.managers import DictProxy, ListProxy, SyncManager
from typing import Dict, List, Optional, Union

from smartutils.design._class import MyBase
from smartutils.design.container.abstract import (
    AbstractPriorityContainer,
    PriorityItemWrap,
    PriorityItemWrapT,
)
from smartutils.error.sys import LibraryUsageError
from smartutils.log import logger


class DictListPriorityContainer(AbstractPriorityContainer[PriorityItemWrapT], MyBase):
    """
    基于 dict+list 实现的优先级容器，支持如下功能：
        - O(1) 取出/删除优先级最小或最大元素。
        - O(1) 删除指定实例。
        - 支持优先级重复（同一优先级可以有多个实例）。
        - 通过简单的 dict/list 管理结构，便于理解和扩展。
        - 易于继承扩展为支持不同算法或持久化的容器实现。

    适合内存中中小规模数据的高性能优先级任务或对象排队场景。
    """

    def __init__(self, manager: Optional[SyncManager] = None, reuse: bool = False):
        # 优先级->实例ID列表
        self._pri_ids_map: Union[Dict[int, List[str]], DictProxy]
        # 有序保存全部优先级，便于O(1)访问最小/最大。
        self._all_pris: Union[List[int], ListProxy]
        # 实例ID -> PriorityItemWrap
        self._id_item_map: Union[Dict[str, PriorityItemWrap], DictProxy]
        self._value2id: Union[Dict[object, str], DictProxy]

        self._manager = manager
        self._reuse = reuse
        if manager is not None:
            # 使用manager生成可进程间共享的dict和list
            self._pri_ids_map = manager.dict()
            self._all_pris = manager.list()
            self._id_item_map = manager.dict()
            self._value2id = manager.dict()
        else:
            self._pri_ids_map = {}
            self._all_pris = []
            self._id_item_map = {}
            self._value2id = {}

        super().__init__()

    def _add_priority(self, priority: int) -> None:
        """
        为指定优先级新增一条空列表，自动判断是否用 manager.list()
        """
        if self._manager is not None:
            self._pri_ids_map[priority] = self._manager.list()  # type: ignore
        else:
            self._pri_ids_map[priority] = []

    def put(self, value: object, priority: int):
        """
        添加一个元素

        参数：
            priority: 定义元素优先级，优先级数字越小，优先级越高。
            value: 元素本身。
        """
        if priority not in self._pri_ids_map:
            # 考虑bitsect
            idx = 0
            while idx < len(self._all_pris) and self._all_pris[idx] < priority:
                idx += 1
            self._all_pris.insert(idx, priority)
            self._add_priority(priority)

        item: PriorityItemWrap = PriorityItemWrap(
            value=value, priority=priority, inst_id=self._value2id.get(value)
        )
        if self._reuse:
            self._value2id[value] = item.inst_id

        self._pri_ids_map[priority].append(item.inst_id)
        self._id_item_map[item.inst_id] = item

    def _pop_end(self, from_min: bool) -> Optional[object]:
        """
        内部通用弹出方法，同优先级，LIFO
        参数:
            from_min: True 取出最小优先级，False 取出最大优先级。
        返回:
            (实例ID, 实例对象)；若队列为空返回 None。
        """
        if not self._all_pris:
            if self._value2id:
                logger.error(
                    "{name} {ids} all in use.",
                    name=self.name,
                    ids=self._value2id.values(),
                )
            else:
                logger.error("{name} no instance, call put first.", name=self.name)
            return None

        pos = 0 if from_min else -1
        pri = self._all_pris[pos]
        ids = self._pri_ids_map[pri]
        inst_id = ids.pop(-1)
        item = self._id_item_map.pop(inst_id)
        if not ids:
            # 该优先级没有实例了
            self._pri_ids_map.pop(pri, None)
            self._all_pris.pop(pos)

        return item.value

    def pop_min(self) -> Optional[object]:
        """
        取出并删除优先级最小的实例。
        """
        return self._pop_end(True)

    def pop_max(self) -> Optional[object]:
        """
        取出并删除优先级最大的实例。
        """
        return self._pop_end(False)

    def remove(self, value: object) -> Optional[object]:
        """
        删除对象。
        返回：
            被删除的实例对象；未找到返回None。
        """
        if not self._reuse:
            raise LibraryUsageError(f"{self.name} not in reuse mode, cant remove.")
        if value not in self._value2id:
            return None

        inst_id = self._value2id.pop(value)
        item = self._id_item_map.pop(inst_id, None)
        if item is None:  # pragma: no cover
            return None

        priority = item.priority
        ids = self._pri_ids_map.get(priority)
        if ids is not None:
            if inst_id in ids:
                ids.remove(inst_id)

            if not ids:
                # 该优先级已经无元素，彻底移除
                self._pri_ids_map.pop(priority, None)
                if priority in self._all_pris:
                    self._all_pris.remove(priority)

        return item.value

    def clear(self) -> None:
        self._pri_ids_map.clear()
        del self._all_pris[:]
        self._id_item_map.clear()
        self._value2id.clear()
        self._manager = None

    def __len__(self) -> int:
        """
        获取容器内元素数量。
        """
        return len(self._id_item_map)
