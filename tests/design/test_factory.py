from typing import Callable

import pytest

from smartutils.design.factory import BaseFactory, Entry
from smartutils.error.sys import LibraryUsageError


class MyMeta:
    def __init__(self, info):
        self.info = info


class TestFactoryNoneMeta(BaseFactory[str, Callable[[], int], None]):
    pass


class TestFactoryWithMeta(BaseFactory[str, Callable[[], int], MyMeta]):
    pass


def setup_module(module):
    # 初始化时清空所有注册
    TestFactoryNoneMeta.reset()
    TestFactoryWithMeta.reset()


def test_register_without_meta():
    """测试: MetaT 为 None, 使用 register 注册和获取普通 Callable, 不含 meta/info"""
    TestFactoryNoneMeta.reset()

    @TestFactoryNoneMeta.register("a")
    def val_a():
        return 1

    @TestFactoryNoneMeta.register("b")
    def val_b():
        return 2

    # 覆盖只能注册一次
    with pytest.raises(Exception):

        @TestFactoryNoneMeta.register("a")
        def another():
            return 999

    assert TestFactoryNoneMeta.get("a")() == 1
    assert TestFactoryNoneMeta.get("b")() == 2


def test_register_with_meta():
    """测试: MetaT 不为 None，注册时传 meta，Entry 保存 meta 信息"""
    TestFactoryWithMeta.reset()
    m = MyMeta("meta-info")

    @TestFactoryWithMeta.register("x", meta=m)
    def val_x():
        return 10

    entry = TestFactoryWithMeta.get_entry("x")
    assert isinstance(entry, Entry)
    assert entry.v() == 10
    assert entry.meta == m


def test_register_with_order():
    """测试: 带 order 参数注册多个 Callable，order 顺序正确"""
    TestFactoryNoneMeta.reset()

    @TestFactoryNoneMeta.register("first", order=0)
    def val_first():
        return 1

    @TestFactoryNoneMeta.register("second", order=10)
    def val_second():
        return 2

    @TestFactoryNoneMeta.register("mid", order=5)
    def val_mid():
        return 3

    keys = [k for k, _ in TestFactoryNoneMeta.all_entries()]
    assert keys == ["first", "mid", "second"]


def test_register_with_deps():
    """测试: 带 deps 注册，依赖顺序正确（a→b→c）"""
    TestFactoryNoneMeta.reset()

    @TestFactoryNoneMeta.register("a")
    def a():
        return 1

    @TestFactoryNoneMeta.register("b", deps=["a"])
    def b():
        return 2

    @TestFactoryNoneMeta.register("c", deps=["b"])
    def c():
        return 3

    keys = [k for k, _ in TestFactoryNoneMeta.all_entries()]
    assert keys == ["a", "b", "c"]


def test_register_with_order_and_deps_respects_topological_and_order():
    """测试: 同时包含 order 和 deps，order 和依赖均生效且无环"""
    TestFactoryNoneMeta.reset()

    @TestFactoryNoneMeta.register("d", order=0)
    def d():
        return 1

    @TestFactoryNoneMeta.register("c", order=1)
    def c():
        return 2

    @TestFactoryNoneMeta.register("b", order=2)
    def b():
        return 3

    @TestFactoryNoneMeta.register("a", order=3)
    def a():
        return 4

    @TestFactoryNoneMeta.register("e", deps=["d"])
    def e():
        return 5

    @TestFactoryNoneMeta.register("f", deps=["c"])
    def f():
        return 6

    # e 必须在 d 后，f 必须在 c 后，但整体依赖和 order 保证没有环
    keys = [k for k, _ in TestFactoryNoneMeta.all_entries()]
    idx = {k: i for i, k in enumerate(keys)}
    assert idx["d"] < idx["e"]
    assert idx["c"] < idx["f"]
    # 其余顺序保持 order（即a>b>c>d）
    assert keys.index("b") > keys.index("c")
    assert keys.index("a") > keys.index("b")


def test_all_and_all_entries_value_consistency():
    """测试: all_entries 的 key 顺序与 all 返回值一致"""
    TestFactoryNoneMeta.reset()

    @TestFactoryNoneMeta.register("x")
    def x():
        return 1

    @TestFactoryNoneMeta.register("y", order=1)
    def y():
        return 2

    @TestFactoryNoneMeta.register("z", order=2)
    def z():
        return 3

    all_keys = [k for k, _ in TestFactoryNoneMeta.all_entries()]
    all_vals = [v() for _, v in TestFactoryNoneMeta.all()]
    # 验证 all_entries 与 all 一致
    assert all_vals == [TestFactoryNoneMeta.get_entry(k).v() for k in all_keys]


def test_get_missing_entry():
    """测试: 获取未注册 key 抛异常"""
    TestFactoryNoneMeta.reset()
    with pytest.raises(LibraryUsageError) as exc:
        TestFactoryNoneMeta.get("missing")

    assert str(exc.value) == "[TestFactoryNoneMeta] key missing not registered."

    with pytest.raises(LibraryUsageError) as exc:
        TestFactoryNoneMeta.get_entry("missing")
    assert str(exc.value) == "[TestFactoryNoneMeta] key missing not registered."

    @TestFactoryNoneMeta.register("a", deps=["b"])
    def a():
        return 1

    with pytest.raises(LibraryUsageError) as exc:
        TestFactoryNoneMeta.all()
    assert str(exc.value) == "[TestFactoryNoneMeta] require register b for register a."


def test_reset():
    """测试: reset 后注册注册内容被清空，获取报错"""
    TestFactoryNoneMeta.reset()

    @TestFactoryNoneMeta.register("key")
    def f():
        return 123

    TestFactoryNoneMeta.reset()
    with pytest.raises(Exception):
        TestFactoryNoneMeta.get("key")
