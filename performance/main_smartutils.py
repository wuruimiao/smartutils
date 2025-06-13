import statistics
import time
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

from fastapi import FastAPI

from smartutils.app import AppHook, run
from smartutils.app.adapter.middleware.starletee import StarletteMiddleware
from smartutils.app.adapter.req.starlette import StarletteRequestAdapter
from smartutils.app.adapter.resp.starlette import StarletteResponseAdapter
from smartutils.app.plugin.exception import ExceptionPlugin
from smartutils.app.plugin.header import HeaderPlugin
from smartutils.app.plugin.log import LogPlugin
from smartutils.ctx import CTXVarManager


# 性能统计收集器
class PerfStats:
    def __init__(self):
        self.stats = defaultdict(list)

    @contextmanager
    def measure(self, name):
        start = time.perf_counter()
        try:
            yield
        finally:
            end = time.perf_counter()
            self.stats[name].append((end - start) * 1000)

    def report(self):
        print("\n=== Performance Report ===")
        for name, times in sorted(self.stats.items()):
            avg = statistics.mean(times)
            median = statistics.median(times)
            p95 = statistics.quantiles(times, n=20)[18]  # 95th percentile
            print(f"{name}:")
            print(f"  Avg: {avg:.2f}ms")
            print(f"  Median: {median:.2f}ms")
            print(f"  P95: {p95:.2f}ms")
            print(f"  Samples: {len(times)}")
            print()


perf_stats = PerfStats()


# 包装中间件以添加性能测量
original_header_dispatch = HeaderPlugin.dispatch


async def header_dispatch(self, req, next_adapter):
    with perf_stats.measure("HeaderPlugin.dispatch"):
        return await original_header_dispatch(self, req, next_adapter)


HeaderPlugin.dispatch = header_dispatch

original_log_dispatch = LogPlugin.dispatch


async def log_dispatch(self, req, next_adapter):
    with perf_stats.measure("LogPlugin.dispatch"):
        return await original_log_dispatch(self, req, next_adapter)


LogPlugin.dispatch = log_dispatch

original_exception_dispatch = ExceptionPlugin.dispatch


async def exception_dispatch(self, req, next_adapter):
    with perf_stats.measure("ExceptionPlugin.dispatch"):
        return await original_exception_dispatch(self, req, next_adapter)


ExceptionPlugin.dispatch = exception_dispatch

# 包装请求适配器
original_req_init = StarletteRequestAdapter.__init__


def req_init(self, request):
    with perf_stats.measure("RequestAdapter.init"):
        original_req_init(self, request)


StarletteRequestAdapter.__init__ = req_init

# 包装响应适配器
original_resp_init = StarletteResponseAdapter.__init__


def resp_init(self, response):
    with perf_stats.measure("ResponseAdapter.init"):
        original_resp_init(self, response)


StarletteResponseAdapter.__init__ = resp_init

# 包装中间件调用
original_middleware_dispatch = StarletteMiddleware.dispatch  # type: ignore


async def middleware_dispatch(self, request, call_next):
    with perf_stats.measure("Middleware.dispatch"):
        return await original_middleware_dispatch(self, request, call_next)


StarletteMiddleware.dispatch = middleware_dispatch  # type: ignore

# 包装上下文管理器
original_use = CTXVarManager.use


@wraps(original_use)
def wrapped_use(*args, **kwargs):
    with perf_stats.measure("CTXVarManager.use"):
        return original_use(*args, **kwargs)


CTXVarManager.use = staticmethod(wrapped_use)


@AppHook.on_startup
async def init_app(app: FastAPI):
    @app.get("/")
    async def root():
        with perf_stats.measure("Handler"):
            return {"hello": "world"}

    @app.get("/stats")
    async def get_stats():
        perf_stats.report()
        return {
            "stats": {
                k: {
                    "avg": statistics.mean(v),
                    "median": statistics.median(v),
                    "p95": statistics.quantiles(v, n=20)[18],
                    "samples": len(v),
                }
                for k, v in perf_stats.stats.items()
            }
        }


if __name__ == "__main__":
    run()
