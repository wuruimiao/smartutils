import functools
import inspect
from typing import Callable, Optional


def proxy_wrapper(
    func: Callable, pre: Optional[Callable] = None, post: Optional[Callable] = None
):
    """
    通用同步/异步/混合协程装饰器，支持Union[Awaitable, Any]返回值:
    - pre(args, kwargs) -> (args, kwargs)
    - post(result, args, kwargs) -> new_result
    """

    @functools.wraps(func)
    def universal_wrapper(*args, **kwargs):
        args1, kwargs1 = pre(args, kwargs) if pre else (args, kwargs)
        result = func(*args1, **kwargs1)
        if inspect.isawaitable(result):

            async def async_inner():
                awaited = await result
                return post(awaited, args, kwargs) if post else awaited

            return async_inner()
        else:
            return post(result, args, kwargs) if post else result

    return universal_wrapper
