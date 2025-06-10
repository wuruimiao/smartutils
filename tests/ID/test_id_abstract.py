from smartutils.ID.abstract import AbstractIDGenerator


class DummyID(AbstractIDGenerator):
    def __init__(self):
        self._called = 0

    def __next__(self):
        self._called += 1
        return self._called

    def __repr__(self):
        return f"DummyID({self._called})"


def test_iter_and_call():
    d = DummyID()
    # __iter__ should return self
    assert iter(d) is d
    # __call__ invokes __next__
    assert d() == 1
    assert d() == 2
    # next/d call should increment
    assert next(d) == 3
    # __repr__ coverage
    assert repr(d) == "DummyID(3)"
