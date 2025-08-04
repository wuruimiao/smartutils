from multiprocessing import Manager, Process, Queue

import pytest

from smartutils.design.container.abstract import AbstractPriorityContainer
from smartutils.design.container.priority_dict_list import DictListPriorityContainer


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
    id1 = container.put(10, "v1")
    assert len(container) == 1
    id2 = container.put(5, "v2")
    assert len(container) == 2
    id3 = container.put(10, "v3")
    assert len(container) == 3
    # 不同优先级与同优先级能并存
    assert id1 != id2 != id3
    # __contains__
    assert id1 in container
    assert id2 in container
    assert "not_exist_id" not in container


def test_pop_min_max(container):
    v = [("a", 5), ("b", 1), ("c", 10)]
    ids = [container.put(pri, val) for val, pri in v]
    # 先2,0,1输入
    pop_id, pop_val = container.pop_min()
    # 最小优先级是1，对应"b"
    assert pop_val == "b"
    assert pop_id == ids[1]
    # 最大优先级是10，对应"c"
    pop_id, pop_val = container.pop_max()
    assert pop_val == "c"
    assert pop_id == ids[2]
    # 剩下"5"
    pop_id, pop_val = container.pop_min()
    assert pop_val == "a"
    assert container.pop_min() is None
    assert container.pop_max() is None


def test_remove(container):
    id_ = container.put(5, "valx")
    assert id_ in container
    v = container.remove(id_)
    assert v == "valx"
    assert id_ not in container
    # 已经删掉再删，返回None
    assert container.remove(id_) is None


def test_repeated_priority(container):
    # 同一优先级多数据，应FIFO弹出
    ids = [container.put(7, f"x{i}") for i in range(3)]
    pop1 = container.pop_min()
    pop2 = container.pop_min()
    pop3 = container.pop_min()
    # 顺序一致
    assert [pop1[1], pop2[1], pop3[1]] == ["x0", "x1", "x2"]
    # 空了
    assert container.pop_min() is None


def test_empty_behavior(container):
    assert container.pop_min() is None
    assert container.pop_max() is None
    assert container.remove("404") is None


def test_remove_valueerror_branch(container, mocker):
    """
    覆盖 remove 方法 except ValueError: pass 分支
    """
    inst_id = container.put(7, "abc")
    priority, idx, value = container._inst_map[inst_id]
    # 伪造 idx 指向不存在（999），并让 pri_list 内无此 inst_id
    container._inst_map[inst_id] = (priority, 999, value)
    pri_list = container._pri_map[priority]
    if inst_id in pri_list:
        pri_list.remove(inst_id)  # 移除之以便接下来找不到
    # Case1: manager模式，可以patch
    if container._manager is not None:
        mocker.patch.object(pri_list, "remove", side_effect=ValueError)
        assert container.remove(inst_id) == "abc"
    else:
        # Case2: 普通list，直接调用 remove 时因没此 inst_id 会抛 ValueError，原代码 except 不报错
        assert container.remove(inst_id) == "abc"


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


def test_multi_process_priority_container():
    with Manager() as manager:
        queue = Queue()
        container = DictListPriorityContainer(manager=manager)
        # 两组操作，一组放入，一组取出
        proc1 = Process(
            target=worker_put_pop,
            args=(
                container,
                queue,
                [("put", 5, "foo"), ("put", 10, "bar"), ("put", 1, "baz")],
            ),
        )
        proc2 = Process(
            target=worker_put_pop, args=(container, queue, [("pop_min",), ("pop_min",)])
        )
        proc1.start()
        proc1.join()
        proc2.start()
        proc2.join()
        # 汇总所有操作看是否一致
        results = [queue.get() for _ in range(5)]
        put_items = [x for x in results if x[0] == "put"]
        pop_items = [x for x in results if x[0] == "pop"]
        assert len(put_items) == 3
        assert len(pop_items) == 2
        popped_values = sorted(
            [v[1][1] for v in pop_items if v[1]]
        )  # 根据优先级出队，结果应为 baz 和 foo
        assert popped_values == ["baz", "foo"]
        # 剩下一个是 bar
        left = container.pop_min()
        assert left is not None and left[1] == "bar"
        # 再弹就空
        assert container.pop_min() is None
