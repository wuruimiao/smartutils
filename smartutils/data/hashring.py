from collections import OrderedDict
from typing import TYPE_CHECKING

from smartutils.log import logger

try:
    from uhashring import HashRing as _HashRing
except ImportError:
    pass
if TYPE_CHECKING:
    from uhashring import HashRing as _HashRing


class HashRing(_HashRing):
    def __init__(self, nodes=None, **kwargs):
        if not nodes:
            nodes = []
        super().__init__(nodes, **kwargs)
        # 环上的真正节点
        self._real_node: list[str] = []
        self._init()

    def _init(self):
        _node_weight = {k: v["weight"] for k, v in self.runtime._nodes.items()}  # noqa
        logger.debug(f"HashRing node weight={_node_weight}")
        # 虚拟节点hash值对应的真实节点
        self._sorted_node = OrderedDict(sorted(self.runtime._ring.items()))  # noqa
        last = None
        for node in self._sorted_node.values():
            if last is not None and node == last:
                continue
            self._real_node.append(node)
            last = node

    def get_node_next_nodes(self, node_name: str) -> list[str]:
        """
        获取真实节点的下一个真实节点，可能有多个
        """
        nodes = []
        for i, name in enumerate(self._real_node):
            if name != node_name:
                continue
            next_i = i + 1
            if next_i == len(self._real_node):
                next_i = 0
            nodes.append(self._real_node[next_i])
        return nodes
