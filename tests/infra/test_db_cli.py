from smartutils.ID.abstract import AbstractIDGenerator


class DummyIDGen(AbstractIDGenerator):
    def __init__(self):
        self._val = 0

    def __next__(self):
        self._val += 1
        return self._val

    def __repr__(self):
        return f"DummyIDGen(val={self._val})"


def test_iter():
    gen = DummyIDGen()
    assert iter(gen) is gen


def test_call():
    gen = DummyIDGen()
    assert gen() == 1
    assert gen() == 2


def test_repr():
    gen = DummyIDGen()
    repr_str = repr(gen)
    assert "DummyIDGen" in repr_str
