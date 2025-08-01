import sys

import pytest

from smartutils.error.sys import LibraryUsageError, TimeOutError
from smartutils.server.ctx import Context, timeoutd


def test_context_basics(mocker):
    fake_now = 1000

    # 固定 get_now_stamp_float - 保证start和检验点一致
    mocker.patch("smartutils.server.ctx.get_now_stamp_float", lambda: fake_now)
    mocker.patch(
        "smartutils.server.ctx.get_stamp_after", lambda x, second=0: x + second
    )

    ctx = Context(sec=5)
    assert ctx._start == fake_now
    assert ctx._deadline == fake_now + 5
    assert ctx.timeout == 5

    # remain_sec 边界
    mocker.patch("smartutils.server.ctx.get_now_stamp_float", lambda: fake_now + 2)
    assert ctx.remain_sec(fake_now + 2) == 3
    assert ctx.timeoutd(fake_now + 2) is False
    assert ctx.remain_sec(fake_now + 10) == 0
    assert ctx.timeoutd(fake_now + 10) is True


def test_context_remain_sec_clipped(mocker):
    fake_now = 100
    mocker.patch("smartutils.server.ctx.get_now_stamp_float", lambda: fake_now)
    mocker.patch(
        "smartutils.server.ctx.get_stamp_after", lambda x, second=0: x + second
    )
    ctx = Context(1)
    # 时间已超限
    assert ctx.remain_sec(ctx._deadline + 1) == 0  # type: ignore


def test_timeoutd_decorator_default_ret():
    # Context已超时
    ctx = Context(0)

    # 先让timeoutd直接返回True（超时）
    def fake_timeoutd(_now=None):
        return True

    ctx.timeoutd = fake_timeoutd  # type: ignore

    @timeoutd(default_ret="X")
    def foo(ctx=None):
        return "NOTCALLED"

    result = foo(ctx)
    assert result == ("X", TimeOutError)

    @timeoutd()
    def bar(ctx=None):
        return "NOTCALLED"

    result2 = bar(ctx)
    assert result2 == TimeOutError


def test_timeoutd_decorator_success():
    ctx = Context(9999)
    # timeoutd返回False（未超时）
    ctx.timeoutd = lambda now=None: False

    @timeoutd(default_ret="Z")
    def foo(ctx, x):
        return "CALLED" + str(x)

    assert foo(ctx, 1) == "CALLED1"

    # 支持把Context放第一个参数
    def foo2(ctx, y):
        return "A"

    wrapped = timeoutd()(foo2)
    assert wrapped(ctx, 2) == "A"


def test_timeoutd_decorator_no_ctx():
    @timeoutd()
    def foo(x):
        return x

    with pytest.raises(LibraryUsageError):
        foo(1)


def test_context_no_deadline():
    ctx = Context()
    # deadline 为 None 时 remain_sec 应该返回 sys.maxsize
    assert ctx.remain_sec() == sys.maxsize
    # deadline 为 None 时 timeoutd 应该永远返回 False
    assert ctx.timeoutd() is False
