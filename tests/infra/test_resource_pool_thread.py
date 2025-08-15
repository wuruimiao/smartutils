# import threading
# import time

# import pytest

# from smartutils.infra.resource.pool._thread import ThreadPriTSPool


# class DummyClosable:
#     """
#     简单的可关闭资源对象
#     """

#     def __init__(self, name):
#         self.name = name
#         self.closed = False

#     def close(self):
#         self.closed = True

#     def __repr__(self):
#         return f"DummyClosable({self.name})"


# @pytest.fixture
# def pool():
#     p = ThreadPriTSPool()
#     # 直接往池子里加资源
#     for i in range(3):
#         p.release(DummyClosable(f"res{i}"))
#     return p


# def test_acquire_and_release(pool):
#     res = pool.acquire(timeout=1)
#     assert isinstance(res, DummyClosable)
#     assert not res.closed
#     pool.release(res)
#     assert not res.closed


# def test_auto_close_on_release_fail(pool, mocker):
#     # 模拟 put 失败
#     mocker.patch.object(pool._container, "put", return_value=False)
#     res = DummyClosable("failres")
#     pool.release(res)
#     assert res.closed


# def test_threaded_acquire_release(pool):
#     results = []

#     def worker():
#         r = pool.acquire(timeout=1)
#         results.append(r)
#         time.sleep(0.1)
#         pool.release(r)

#     threads = [threading.Thread(target=worker) for _ in range(3)]
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()
#     assert len(results) == 3
#     assert all(isinstance(r, DummyClosable) for r in results)


# def test_use_context_manager(pool):
#     with pool.use(timeout=1) as res:
#         assert isinstance(res, DummyClosable)
#         assert not res.closed
#     # 自动 release 后未关闭（本池不默认 auto-close）
#     assert not res.closed


# def test_close_all(pool, mocker):
#     patch = mocker.patch.object(DummyClosable, "close", autospec=True)

#     # 关闭会自动回收所有还在池中的资源
#     pool.close()
#     # 当前池可无资源（被清空）
#     # 但我们能确保所有 DummyClosable 都被 close
#     # pool._container 是 ConditionContainer
#     assert pool._container._proxy.empty()
#     assert pool._container.empty()
#     assert patch.call_count == 3
