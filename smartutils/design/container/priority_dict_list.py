import uuid
from multiprocessing.managers import DictProxy, ListProxy, SyncManager
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union

from smartutils.design.container.abstract import AbstractPriorityContainer

T = TypeVar("T")


class DictListPriorityContainer(AbstractPriorityContainer[T], Generic[T]):
    """
    基于 dict+list 实现的优先级容器，支持如下功能：
        - O(1) 取出/删除优先级最小或最大元素。
        - O(1) 删除指定实例。
        - 支持优先级重复（同一优先级可以有多个实例）。
        - 通过简单的 dict/list 管理结构，便于理解和扩展。
        - 易于继承扩展为支持不同算法或持久化的容器实现。

    适合内存中中小规模数据的高性能优先级任务或对象排队场景。
    """

    def __init__(self, manager: Optional[SyncManager] = None):
        # _pri_map: 记录每个优先级（int）对应的实例ID列表（先进先出顺序）。
        self._pri_map: Union[Dict[int, List[str]], DictProxy]
        # _all_pris: 有序保存当前所有已存在的优先级，便于O(1)访问最小/最大。
        self._all_pris: Union[List[int], ListProxy]
        # _inst_map: 存储每个实例ID对应的(优先级, 在pri_map优先级列表下标, 实例对象)。
        self._inst_map: Union[Dict[str, Tuple[int, int, T]], DictProxy]

        self._manager = manager
        if manager is not None:
            # 使用manager生成可进程间共享的dict和list
            self._pri_map = manager.dict()
            self._all_pris = manager.list()
            self._inst_map = manager.dict()
        else:
            self._pri_map = {}
            self._all_pris = []
            self._inst_map = {}

    def _add_priority(self, priority: int) -> None:
        """
        为指定优先级新增一条空列表，自动判断是否用 manager.list()
        """
        if self._manager is not None:
            self._pri_map[priority] = self._manager.list()  # type: ignore
        else:
            self._pri_map[priority] = []

    def put(self, priority: int, value: T) -> str:
        """
        添加一个元素到指定优先级队列，并返回其实例ID。

        参数：
            priority: 定义元素优先级，优先级数字越小，优先级越高。
            value: 元素本身。
        返回：
            唯一实例ID，可用于后续删除。
        """
        if priority not in self._pri_map:
            # 若新优先级，则按顺序插入_all_pris，保持优先级有序
            idx = 0
            while idx < len(self._all_pris) and self._all_pris[idx] < priority:
                idx += 1
            self._all_pris.insert(idx, priority)
            self._add_priority(priority)

        inst_id = str(uuid.uuid4())
        pri_list = self._pri_map[priority]
        pri_list.append(inst_id)
        self._inst_map[inst_id] = (priority, len(pri_list) - 1, value)
        return inst_id

    def _pop_end(self, from_min: bool) -> Optional[Tuple[str, T]]:
        """
        内部通用弹出方法。
        参数:
            from_min: True 取出最小优先级，False 取出最大优先级。
        返回:
            (实例ID, 实例对象)；若队列为空返回 None。
        """
        if not self._all_pris:
            return None
        # 根据参数选择首或尾
        pos = 0 if from_min else -1
        pri = self._all_pris[pos]
        pri_list = self._pri_map[pri]
        inst_id = pri_list.pop(0 if from_min else -1)
        _, _, value = self._inst_map.pop(inst_id)
        if not pri_list:
            del self._pri_map[pri]
            self._all_pris.pop(pos)
        return inst_id, value

    def pop_min(self) -> Optional[Tuple[str, T]]:
        """
        取出并删除优先级最小的实例。
        """
        return self._pop_end(True)

    def pop_max(self) -> Optional[Tuple[str, T]]:
        """
        取出并删除优先级最大的实例。
        """
        return self._pop_end(False)

    def remove(self, inst_id: str) -> Optional[T]:
        """
        按实例ID删除对象。
        返回：
            被删除的实例对象；未找到返回None。
        """
        if inst_id not in self._inst_map:
            return None
        priority, idx, value = self._inst_map.pop(inst_id)
        pri_list = self._pri_map[priority]
        # 优化：如果idx失效（并发或外部操作），依然可fallback到remove
        if idx < len(pri_list) and pri_list[idx] == inst_id:
            pri_list.pop(idx)
        else:
            try:
                pri_list.remove(inst_id)
            except ValueError:
                pass
        if not pri_list:
            del self._pri_map[priority]
            self._all_pris.remove(priority)
        return value

    def __len__(self) -> int:
        """
        当前容器内元素总数。
        """
        return len(self._inst_map)

    def __contains__(self, inst_id: str) -> bool:
        """
        是否包含指定实例ID。
        """
        return inst_id in self._inst_map
