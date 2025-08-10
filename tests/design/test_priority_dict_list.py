from multiprocessing import Manager
from typing import List

import pytest

from smartutils.design.pri_container.abstract import (
    PriContainerItemBase,
    PriContainerProtocol,
)
from smartutils.design.pri_container.dict_list import PriContainerDictList
from smartutils.error.sys import ContainerClosedError


@pytest.fixture(params=[None, Manager])
def container(request):
    """
    分别测试单进程与多进程容器（后者用 multiprocessing.Manager）
    """
    proc_manager = None
    if request.param is None:
        c = PriContainerDictList()
        assert isinstance(c, PriContainerProtocol)
        yield c
    else:
        proc_manager = Manager()
        c = PriContainerDictList(manager=proc_manager)
        assert isinstance(c, PriContainerProtocol)
        yield c
        proc_manager.shutdown()


class Item(PriContainerItemBase):
    def before_put(self):
        self._priority = self.value

    def after_get(self): ...


def test_put_and_len(container):
    items = []
    for i in [3, 2, 1]:
        item = Item(i)
        container.put(item)
        items.append(item)

    assert len(container) == 3

    for item in items:
        assert item in container

    assert container.empty() is False

    ids = [item.inst_id for item in items]
    for item in container:
        assert item.inst_id in ids


def test_pop_min_max(container):
    items: List[Item] = []
    for i in [3, 2, 1]:
        item = Item(i)
        container.put(item)
        items.append(item)

    item: Item = container.get_min()
    assert item
    assert item.value == 1
    item = container.get_max()
    assert item.value == 3
    item = container.get_min()
    assert item.value == 2
    assert container.get_min() is None
    assert container.get_max() is None


def test_get(container):
    items: List[Item] = []
    for i in [3, 2, 1]:
        item = Item(i)
        container.put(item)
        items.append(item)

    item: Item = container.get()
    assert item.value == 3
    item = container.get()
    assert item.value == 2
    assert container.get_min().value == 1
    assert container.get_max() is None


def test_empty_behavior(container):
    assert container.get_min() is None
    assert container.get_max() is None


def test_pri_dict_list_close(container):
    container.put(Item(1))
    assert container.close() is None
    assert container.closed
    assert len(container) == 0

    with pytest.raises(ContainerClosedError):
        assert container.put(Item(2)) is False
    with pytest.raises(ContainerClosedError):
        assert container.get_max() is None
