import pytest

from smartutils.design.module import require_modules
from smartutils.error.sys import LibraryUsageError


def test_require_modules_all_installed():
    @require_modules(a=object(), b="str")
    def foo():
        return "ok"

    assert foo() == "ok"


def test_require_modules_some_missing():
    @require_modules(a=None, b=object())
    def bar():
        return "ok"

    with pytest.raises(LibraryUsageError) as e:
        bar()
    assert "a" in str(e.value)
    assert "Required module" in str(e.value)


def test_require_modules_multiple_missing():
    @require_modules(a=None, b=None)
    def baz():
        return "fail"

    with pytest.raises(LibraryUsageError) as e:
        baz()
    # 两个变量名都应在异常信息中
    assert "a" in str(e.value)
    assert "b" in str(e.value)
