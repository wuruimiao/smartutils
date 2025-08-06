from multiprocessing import Manager

import pytest

from smartutils.design.container.abstract_pri import (
    PriContainerProtocol,
)
from smartutils.design.container.item import PriItemWrap
from smartutils.design.container.pri_dict_list import PriContainerDictList
from smartutils.error.sys import LibraryUsageError


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


@pytest.fixture(params=[None, Manager])
def reuse_container(request):
    """
    分别测试单进程与多进程容器（后者用 multiprocessing.Manager）
    """
    proc_manager = None
    if request.param is None:
        c = PriContainerDictList(reuse=True)
        assert isinstance(c, PriContainerProtocol)
        yield c
    else:
        proc_manager = Manager()
        c = PriContainerDictList(manager=proc_manager, reuse=True)
        assert isinstance(c, PriContainerProtocol)
        yield c
        proc_manager.shutdown()


def test_put_and_len(container):
    container.push("v1", 10)
    assert len(container) == 1
    container.push("v2", 5)
    assert len(container) == 2
    container.push("v3", 10)
    assert len(container) == 3

    assert "v1" in container
    assert "v2" in container
    assert "v3" in container

    assert container.is_empty() is False

    for value in container:
        assert value in {"v1", "v2", "v3"}


def test_with_auto_close():
    with PriContainerDictList() as container:
        container.push("v1", 10)
        assert len(container) == 1
        container.push("v2", 5)
        assert len(container) == 2
        container.push("v3", 10)
        assert len(container) == 3

        assert "v1" in container
        assert "v2" in container
        assert "v3" in container

        assert container.is_empty() is False

        for value in container:
            assert value in {"v1", "v2", "v3"}

    assert container.is_empty() is True


def test_pop_min_max(container):
    v = [("a", 5), ("b", 1), ("c", 10)]
    [container.push(val, pri) for val, pri in v]
    # 先2,0,1输入
    pop_val = container.pop_min()
    # 最小优先级是1，对应"b"
    assert pop_val == "b"
    # 最大优先级是10，对应"c"
    pop_val = container.pop_max()
    assert pop_val == "c"
    # 剩下"5"
    pop_val = container.pop_min()
    assert pop_val == "a"
    assert container.pop_min() is None
    assert container.pop_max() is None


def test_get(container):
    v = [("a", 5), ("b", 1), ("c", 10)]
    [container.push(val, pri) for val, pri in v]
    pop_val = container.get()
    # 最大优先级是"c"
    assert pop_val == "c"
    # 最大优先级是"a"
    pop_val = container.get()
    assert pop_val == "a"
    assert container.pop_min() == "b"
    assert container.pop_max() is None


def test_put(container):
    container.put("a")
    container.put("b")
    container.put("c")
    assert len(container) == 3


def test_cant_remove(container):
    with pytest.raises(LibraryUsageError) as e:
        container.push("valx", 5)
        container.remove("valx")
    assert str(e.value) == "[PriContainerDictList] not in reuse mode, cant remove."


def test_repeated_priority(container):
    # 同一优先级多数据，应LIFO弹出
    [container.push(f"x{i}", 7) for i in range(3)]
    pop1 = container.pop_min()
    pop2 = container.pop_min()
    pop3 = container.pop_min()
    # 顺序一致
    assert [pop1, pop2, pop3] == ["x2", "x1", "x0"]
    # 空了
    assert container.pop_min() is None


def test_empty_behavior(container):
    assert container.pop_min() is None
    assert container.pop_max() is None


def test_priority_item_str():
    item = PriItemWrap(value=1, priority=2, inst_id="3")
    assert str(item) == "<[PriItemWrap] id=3 cnt=0 val=1> priority=2"
    assert item.inst_id == "3"
    assert item.value == 1


def test_remove(reuse_container):
    reuse_container.push("valx", 5)
    assert reuse_container.remove("valx") == "valx"
    assert reuse_container.pop_max() is None
    assert reuse_container.remove("valx") is None


def test_pop_max(reuse_container):
    reuse_container.push("valx", 5)
    assert "valx" in reuse_container
    assert reuse_container.pop_max() == "valx"
    assert reuse_container.pop_max() is None


def test_pri_dict_list_close(container):
    container.push(1, 2)
    assert container.close() == [1]
    assert len(container) == 0

    with pytest.raises(LibraryUsageError) as e:
        assert container.pop_max() is None
    assert str(e.value) == "[PriContainerDictList] closed, no operations allowed."
