import pytest

from smartutils.design.factory import BaseFactory
from smartutils.error.sys import LibraryError, LibraryUsageError


class CustomTestFactory(BaseFactory[str, int]):
    pass


def test_factory_with_deps_no_dep():
    with pytest.raises(LibraryError) as e:
        CustomTestFactory.register("test1", deps=["test"])(1)
    assert (
        str(e.value)
        == "[CustomTestFactory] require register test before register test1."
    )


def test_factory_register_more_then_one():
    CustomTestFactory.register("test2")(1)
    with pytest.raises(LibraryError) as e:
        CustomTestFactory.register("test2")(2)
    assert str(e.value) == "[CustomTestFactory] key test2 already registered."


def test_factory_register_with_dep_and_order():
    with pytest.raises(LibraryError) as e:
        CustomTestFactory.register("test3", deps=["test1"], order=1)(3)
    assert (
        str(e.value)
        == "[CustomTestFactory] key test3 order or deps, cannot set together."
    )


def test_factory_get_no_key():
    with pytest.raises(LibraryUsageError) as e:
        CustomTestFactory.get("test4")
    assert str(e.value) == "[CustomTestFactory] key test4 not registered."


def test_factory_reset():
    CustomTestFactory.register("test5")(1)
    CustomTestFactory.reset()
    with pytest.raises(LibraryUsageError) as e:
        CustomTestFactory.get("test5")
    assert str(e.value) == "[CustomTestFactory] key test5 not registered."


def test_factory_deps_check():
    CustomTestFactory.register("test6")(1)
    CustomTestFactory.register("test7", deps=["test6"], check_deps=True)(1)
