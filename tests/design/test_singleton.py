import threading
from unittest.mock import patch

from smartutils.design import SingletonBase, SingletonMeta, singleton


@singleton
class DecoratorSingleton:
    def __init__(self, value=0):
        self.value = value


def test_decorator_singleton_basic():
    a = DecoratorSingleton(1)
    b = DecoratorSingleton(2)
    assert a is b
    assert a.value == 1
    assert b.value == 1


def test_decorator_singleton_threadsafe():
    results = []

    def create_instance():
        results.append(DecoratorSingleton(42))

    threads = [threading.Thread(target=create_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(obj is results[0] for obj in results)


class BaseSingleton(SingletonBase):
    def _init_once(self, value=0):
        self.value = value


def test_base_singleton_basic():
    a = BaseSingleton(10)
    b = BaseSingleton(20)
    assert a is b
    assert a.value == 10  # type: ignore
    assert b.value == 10  # type: ignore


def test_base_singleton_threadsafe():
    results = []

    def create_instance():
        results.append(BaseSingleton(99))

    threads = [threading.Thread(target=create_instance) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(obj is results[0] for obj in results)


class MetaSingleton(metaclass=SingletonMeta):
    def __init__(self, value=0):
        self.value = value


def test_meta_singleton_basic():
    a = MetaSingleton(123)
    b = MetaSingleton(456)
    assert a is b
    assert a.value == 123
    assert b.value == 123


def test_meta_singleton_threadsafe():
    results = []

    def create_instance():
        results.append(MetaSingleton(888))

    threads = [threading.Thread(target=create_instance) for _ in range(15)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(obj is results[0] for obj in results)


def test_decorator_singleton_reset():
    a = DecoratorSingleton(1)
    DecoratorSingleton.reset()  # type: ignore
    b = DecoratorSingleton(2)
    assert a is not b
    assert b.value == 2


async def test_decorator_singleton_reset_all():
    a = DecoratorSingleton(10)
    from smartutils.design.singleton import reset_all

    reset_all()
    b = DecoratorSingleton(20)
    assert a is not b
    assert b.value == 20


def test_base_singleton_reset():
    a = BaseSingleton(5)
    BaseSingleton.reset()
    b = BaseSingleton(6)
    assert a is not b
    assert b.value == 6  # type: ignore


def test_base_singleton_reset_all():
    a = BaseSingleton(7)
    SingletonBase.reset_all()
    b = BaseSingleton(8)
    assert a is not b
    assert b.value == 8  # type: ignore


def test_meta_singleton_reset():
    a = MetaSingleton(11)
    MetaSingleton.reset()
    b = MetaSingleton(12)
    assert a is not b
    assert b.value == 12


def test_meta_singleton_reset_all():
    a = MetaSingleton(13)
    MetaSingleton.reset_all()
    b = MetaSingleton(14)
    assert a is not b
    assert b.value == 14


class CounterSingleton(SingletonBase):
    init_count = 0

    def _init_once(self, value=0):
        type(self).init_count += 1
        self.value = value


def test_base_singleton_init_once_called_once():
    CounterSingleton.reset()
    CounterSingleton.init_count = 0

    a = CounterSingleton(100)
    b = CounterSingleton(200)
    assert a is b
    assert a.value == 100  # type: ignore
    assert b.value == 100  # type: ignore
    assert CounterSingleton.init_count == 1

    CounterSingleton.reset()
    c = CounterSingleton(300)
    assert c is not a
    assert c.value == 300  # type: ignore
    assert CounterSingleton.init_count == 2
