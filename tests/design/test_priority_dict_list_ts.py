# from multiprocessing import Manager

# import pytest

# from smartutils.design.pri_container.abstract import PriContainerProtocol
# from smartutils.design.pri_container.imp import PriTSContainerDictList
# from smartutils.error.sys import LibraryUsageError


# @pytest.fixture(params=[None, Manager])
# def container(request):
#     """
#     分别测试单进程与多进程容器（后者用 multiprocessing.Manager）
#     """
#     proc_manager = None
#     if request.param is None:
#         c = PriTSContainerDictList()
#         assert isinstance(c, PriContainerProtocol)
#         yield c
#     else:
#         proc_manager = Manager()
#         c = PriTSContainerDictList(manager=proc_manager)
#         assert isinstance(c, PriContainerProtocol)
#         yield c
#         proc_manager.shutdown()


# def test_put_and_len(container):
#     assert container.put("v1")
#     assert len(container) == 1
#     assert container.put("v2")
#     assert len(container) == 2
#     assert container.put("v3")
#     assert len(container) == 3

#     assert "v1" in container
#     assert "v2" in container
#     assert "v3" in container

#     assert container.empty() is False

#     for value in container:
#         assert value in {"v1", "v2", "v3"}


# def test_pop_min_max(container):
#     v = [("a", 5), ("b", 1), ("c", 10)]
#     [container.put(val, pri) for val, pri in v]
#     # 先2,0,1输入
#     pop_val = container.get_min()
#     # 最小优先级是1，对应"b"
#     assert pop_val == "b"
#     # 最大优先级是10，对应"c"
#     pop_val = container.get_max()
#     assert pop_val == "c"
#     # 剩下"5"
#     pop_val = container.get_min()
#     assert pop_val == "a"
#     assert container.get_min() is None
#     assert container.get_max() is None


# def test_get(container):
#     v = [("a", 5), ("b", 1), ("c", 10)]
#     [container.put(val) for val, pri in v]
#     pop_val = container.get()
#     # 最大优先级是"c"
#     assert pop_val == "c"
#     # 最大优先级是"a"
#     pop_val = container.get()
#     assert pop_val == "a"
#     assert container.get_min() == "b"
#     assert container.get_max() is None


# def test_put(container):
#     container.put("a")
#     container.put("b")
#     container.put("c")
#     assert len(container) == 3


# def test_cant_remove(container):
#     with pytest.raises(LibraryUsageError) as e:
#         container.put("valx")
#         container.remove("valx")
#     assert str(e.value) == "[PriTSContainerDictList] not in reuse mode, cant remove."


# def test_repeated_priority(container):
#     # 同一优先级多数据，应LIFO弹出
#     [container.put(f"x{i}") for i in range(3)]
#     pop1 = container.get_min()
#     pop2 = container.get_min()
#     pop3 = container.get_min()
#     # 顺序一致
#     assert [pop1, pop2, pop3] == ["x2", "x1", "x0"]
#     # 空了
#     assert container.get_min() is None


# def test_empty_behavior(container):
#     assert container.get_min() is None
#     assert container.get_max() is None


# def test_remove(reuse_container):
#     reuse_container.put("valx")
#     assert reuse_container.remove("valx") == "valx"
#     assert reuse_container.get_max() is None
#     assert reuse_container.remove("valx") is None


# def test_pop_max(reuse_container):
#     reuse_container.put("valx")
#     assert "valx" in reuse_container
#     assert reuse_container.get_max() == "valx"
#     assert reuse_container.get_max() is None


# def test_pri_dict_list_close(container):
#     container.put(1)
#     assert container.close() is None
#     assert container.closed
#     assert len(container) == 0

#     assert container.put(2) is False
#     assert container.put(3) is False
#     assert container.get_max() is None
#     assert container.remove(1) is None
