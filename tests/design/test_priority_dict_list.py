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


def test_pri_container_dict_list_item():
    item = Item(1)
    assert str(item) == f"[Item]<{item.inst_id}>"


def test_pri_container_dict_list_put_and_len(container):
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


def test_pri_container_dict_list_pop_min_max(container):
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


def test_pri_container_dict_list_get(container):
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


def test_pri_container_dict_list_empty_behavior(container):
    assert container.get_min() is None
    assert container.get_max() is None


def test_pri_container_dict_list__close(container):
    container.put(Item(1))
    assert container.close() is None
    assert container.closed
    assert len(container) == 0

    with pytest.raises(ContainerClosedError):
        assert container.put(Item(2)) is False
    with pytest.raises(ContainerClosedError):
        assert container.get_max() is None


def test_pri_container_dict_list_put_exist(container, mocker):
    item = Item(1)
    container.put(item)
    assert item in container
    assert item.inst_id in container._idles
    item2 = Item(2)
    # Patch item2 的 inst_id 属性，使用 PropertyMock
    from unittest.mock import PropertyMock

    mocker.patch.object(
        type(item2), "inst_id", new_callable=PropertyMock, return_value=item.inst_id
    )
    container.put(item2)
    assert item2 in container


def test_pri_container_dict_list_put_using(container):
    item = Item(1)
    container.put(item)
    assert item in container

    item2 = container.get()
    assert item2.inst_id == item.inst_id
    assert item.inst_id in container._usings

    container.put(item2)
    assert item.inst_id in container._idles


def test_pri_container_dict_list_remove(container):
    item = Item(1)
    container.put(item)
    assert item in container

    item2 = container.remove(item)
    assert item.inst_id == item2.inst_id
    assert item.value == item2.value

    assert item not in container
    assert item2 not in container


def test_pri_container_dict_list_remove_using(container):
    item = Item(1)
    container.put(item)
    assert item in container

    item3 = container.get()
    assert item.inst_id == item3.inst_id
    assert item in container
    assert item3 in container

    assert container.remove(item) is None

    assert item in container
    assert item3 in container


def test_pri_container_dict_list_remove_none(container):
    assert container.remove(Item("not_exist")) is None


def test_pri_container_dict_list_obj_not_base(container):
    assert "not container item base" not in container


def test_pri_container_dict_list_iter(container):
    container.put(Item(1))
    container.put(Item(2))
    container.get()

    for item in container:
        assert item.value in (1, 2)


def test_pri_container_dict_list_full(container):
    assert container.full() is False
