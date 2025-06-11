import pytest

from smartutils.ID.abstract import AbstractIDGenerator


class DummyIDGen(AbstractIDGenerator):
    def __init__(self):
        self.cur = 0

    def __next__(self):
        self.cur += 1
        return self.cur

    def __repr__(self):
        return f"TestIDGen({self.cur})"


def test_iter_and_call():
    g = DummyIDGen()
    # __iter__应返回自身
    assert iter(g) is g
    # __call__内部等价于next(g)
    assert g() == 1
    assert next(g) == 2
    assert repr(g) == "TestIDGen(2)"


def test_abstract_cannot_instantiate():
    # 抽象类不能直接实例化
    with pytest.raises(TypeError):
        AbstractIDGenerator()
