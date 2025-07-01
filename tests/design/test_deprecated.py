import warnings

from smartutils.design.deprecated import deprecated


def test_deprecated_emits_warning():
    @deprecated("new_func")
    def old_func(x):
        return x * 2

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old_func(3)
        assert result == 6
        assert len(w) == 1
        warning = w[0]
        assert issubclass(warning.category, DeprecationWarning)
        # 信息里必须有旧和新方法名
        assert "old_func" in str(warning.message)
        assert "new_func" in str(warning.message)


def test_deprecated_multi_funcs():
    @deprecated("bar")
    def foo():
        return "foo"

    @deprecated("baz")
    def bar():
        return "bar"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert foo() == "foo"
        assert bar() == "bar"
        messages = [str(warn.message) for warn in w]
        assert any("foo" in m for m in messages)
        assert any("bar" in m for m in messages)
