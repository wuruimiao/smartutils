from functools import wraps
from smartutils.time import get_now_stamp, get_stamp_after
from smartutils.error.sys import TimeOutError

__all__ = ["Context", "timeoutd"]


class Context:
    def __init__(self, sec: int, start=get_now_stamp()):
        self._start = start
        self._deadline = int(get_stamp_after(self._start, second=sec))
        self.timeout = sec

    def timeoutd(self, now=get_now_stamp()) -> bool:
        return now >= self._deadline

    def remain_sec(self, now=get_now_stamp()) -> int:
        return max(0, self._deadline - now)


def timeoutd(default_ret=None):
    def _decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            ctx: Context = kwargs.get("ctx", None)
            if not ctx and len(args) > 0:
                for arg in args:
                    if not isinstance(arg, Context):
                        continue
                    ctx = arg

            if ctx and ctx.timeoutd():
                if default_ret is not None:
                    return default_ret, TimeOutError
                return TimeOutError
            return func(*args, **kwargs)

        return decorated

    return _decorator
