from smartutils.error.sys import TimeOutError
from smartutils.server.ctx import Context, timeoutd


def test_context_basics(monkeypatch):
    fake_now = 1000

    # 固定 get_now_stamp_float - 保证start和检验点一致
    monkeypatch.setattr("smartutils.server.ctx.get_now_stamp_float", lambda: fake_now)
    monkeypatch.setattr(
        "smartutils.server.ctx.get_stamp_after", lambda x, second=0: x + second
    )

    ctx = Context(sec=5)
    assert ctx._start == fake_now
    assert ctx._deadline == fake_now + 5
    assert ctx.timeout == 5

    # remain_sec 边界
    monkeypatch.setattr(
        "smartutils.server.ctx.get_now_stamp_float", lambda: fake_now + 2
    )
    assert ctx.remain_sec(fake_now + 2) == 3
    assert ctx.timeoutd(fake_now + 2) is False
    assert ctx.remain_sec(fake_now + 10) == 0
    assert ctx.timeoutd(fake_now + 10) is True


def test_context_remain_sec_clipped(monkeypatch):
    fake_now = 100
    monkeypatch.setattr("smartutils.server.ctx.get_now_stamp_float", lambda: fake_now)
    monkeypatch.setattr(
        "smartutils.server.ctx.get_stamp_after", lambda x, second=0: x + second
    )
    ctx = Context(1)
    # 时间已超限
    assert ctx.remain_sec(ctx._deadline + 1) == 0


def test_timeoutd_decorator_default_ret(monkeypatch):
    # Context已超时
    ctx = Context(0)

    # 先让timeoutd直接返回True（超时）
    def fake_timeoutd(_now=None):
        return True

    ctx.timeoutd = fake_timeoutd

    @timeoutd(default_ret="X")
    def foo(ctx=None):
        return "NOTCALLED"

    result = foo(ctx=ctx)
    assert result == ("X", TimeOutError)

    @timeoutd()
    def bar(ctx=None):
        return "NOTCALLED"

    result2 = bar(ctx=ctx)
    assert result2 == TimeOutError


def test_timeoutd_decorator_success(monkeypatch):
    ctx = Context(9999)
    # timeoutd返回False（未超时）
    ctx.timeoutd = lambda now=None: False

    @timeoutd(default_ret="Z")
    def foo(x, ctx=None):
        return "CALLED" + str(x)

    assert foo(1, ctx=ctx) == "CALLED1"

    # 支持把Context放第一个参数
    def foo2(ctx, y):
        return "A"

    wrapped = timeoutd()(foo2)
    assert wrapped(ctx, 2) == "A"


def test_timeoutd_decorator_no_ctx():
    @timeoutd()
    def foo(x):
        return x

    # 无ctx参数时，直接执行被装饰函数
    assert foo(5) == 5
