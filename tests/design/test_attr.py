import pytest

from smartutils.design.attr import RequireAttrs
from smartutils.error.sys import LibraryError


def test_requireattrs_all_defined():
    class Foo(metaclass=RequireAttrs):
        required_attrs = ("bar", "baz")
        bar = 1
        baz = 2

    # 可被成功创建
    assert hasattr(Foo, "bar")
    assert hasattr(Foo, "baz")


def test_requireattrs_missing_attr():
    with pytest.raises(LibraryError) as excinfo:

        class Bar(metaclass=RequireAttrs):
            required_attrs = ("x",)
            # 没有定义x
            ...

    assert "x" in str(excinfo.value)
    assert "Bar" in str(excinfo.value)


def test_requireattrs_default_empty():
    class Baz(metaclass=RequireAttrs): ...

    assert Baz


def test_requireattrs_abstractmethods_skip():
    class Qux(metaclass=RequireAttrs):
        required_attrs = ("y",)
        __abstractmethods__ = True

    # 不会抛异常，即使没定义 y
    assert Qux
