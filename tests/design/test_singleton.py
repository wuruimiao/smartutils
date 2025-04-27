import threading

from smartutils.design import singleton, SingletonBase, SingletonMeta


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
    for t in threads: t.start()
    for t in threads: t.join()
    assert all(obj is results[0] for obj in results)


class BaseSingleton(SingletonBase):
    def _init_once(self, value=0):
        self.value = value


def test_base_singleton_basic():
    a = BaseSingleton(10)
    b = BaseSingleton(20)
    assert a is b
    assert a.value == 10
    assert b.value == 10


def test_base_singleton_threadsafe():
    results = []

    def create_instance():
        results.append(BaseSingleton(99))

    threads = [threading.Thread(target=create_instance) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
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
    for t in threads: t.start()
    for t in threads: t.join()
    assert all(obj is results[0] for obj in results)
