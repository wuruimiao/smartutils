from functools import wraps
from typing import Optional

from smartutils.error.sys import TimeOutError
from smartutils.time import get_now_stamp_float, get_stamp_after

__all__ = ["Context", "timeoutd"]


class Context:
    def __init__(self, sec: int, start=None):
        self._start = start or get_now_stamp_float()
        self._deadline = int(get_stamp_after(self._start, second=sec))
        self.timeout = sec

    def timeoutd(self, now=get_now_stamp_float()) -> bool:
        return now >= self._deadline

    def remain_sec(self, now=get_now_stamp_float()) -> float:
        return max(0, self._deadline - now)


def timeoutd(default_ret=None):
    def _decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            ctx: Optional[Context] = kwargs.get("ctx", None)
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
