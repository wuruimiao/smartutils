from multiprocessing import Manager, Process, Queue

import pytest

from smartutils.design.container.abstract import AbstractPriorityContainer
from smartutils.design.container.priority_dict_list import DictListPriorityContainer
from smartutils.error.sys import LibraryUsageError


@pytest.fixture(params=[None, Manager])
def container(request):
    """
    分别测试单进程与多进程容器（后者用 multiprocessing.Manager）
    """
    proc_manager = None
    if request.param is None:
        c = DictListPriorityContainer()
        assert isinstance(c, AbstractPriorityContainer)
        yield c
    else:
        proc_manager = Manager()
        c = DictListPriorityContainer(manager=proc_manager)
        assert isinstance(c, AbstractPriorityContainer)
        yield c
        proc_manager.shutdown()


def test_put_and_len(container):
    container.put(10, "v1")
    assert len(container) == 1
    container.put(5, "v2")
    assert len(container) == 2
    container.put(10, "v3")
    assert len(container) == 3


def test_pop_min_max(container):
    v = [("a", 5), ("b", 1), ("c", 10)]
    [container.put(val, pri) for val, pri in v]
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


def test_cant_remove(container):
    with pytest.raises(LibraryUsageError) as e:
        container.put("valx", 5)
        v = container.remove("valx")
    assert str(e.value) == "[DictListPriorityContainer] not in reuse mode, cant remove."


def test_repeated_priority(container):
    # 同一优先级多数据，应LIFO弹出
    [container.put(f"x{i}", 7) for i in range(3)]
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


def worker_put_pop(container, q, actions):
    for act in actions:
        if act[0] == "put":
            inst_id = container.put(act[1], act[2])
            q.put(("put", inst_id, act[1], act[2]))
        elif act[0] == "pop_min":
            result = container.pop_min()
            q.put(("pop", result))
        elif act[0] == "remove":
            result = container.remove(act[1])
            q.put(("remove", act[1], result))
