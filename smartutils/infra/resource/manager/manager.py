"""
资源管理器（ResourceManager）核心实现
-----------------------------------------
用于统一管理异步资源（如Redis、数据库等）的获取、释放、异常捕获和拓展钩子，是中大型应用推荐的基础设施组件。

核心特性：
- 资源容器注册与全局管理，批量关闭/重置。
- 使用@mgr.use装饰器包裹业务函数，支持自动上下文切换与强一致异常捕获处理。
- 支持资源成功/失败钩子拓展，异常类型自定义。
- 提供基于上下文变量（CTXVarManager）的当前资源句柄，方便异步隔离。
- 可拓展支持事务等特殊模式。

典型用法：
    mgr = RedisManager()
    @mgr.use
    async def foo():
        await mgr.curr.get('key')

适配场景：
    统一资源生命周期管理、日志/异常收敛、后续便于平台化扩展。
"""

from __future__ import annotations

import asyncio
import functools
from abc import ABC
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    Union,
    overload,
)

from smartutils.call import call_hook
from smartutils.config.const import ConfKey
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import MyBase
from smartutils.error.base import BaseError
from smartutils.error.sys import LibraryUsageError, SysError
from smartutils.infra.resource.abstract import AbstractAsyncResourceT
from smartutils.log import logger

__all__ = ["ResourceManagerRegistry", "CTXResourceManager"]


class ResourceManagerRegistry:
    """
    全局资源管理器注册表。
    用于批量注册已创建的资源管理器实例，方便统一回收/关闭。
    """

    _instances: List[CTXResourceManager] = []

    @classmethod
    def register(cls, instance):
        cls._instances.append(instance)

    @classmethod
    def get_all(cls):
        return list(cls._instances)

    @classmethod
    async def close_all(cls):
        await asyncio.gather(*(mgr.close() for mgr in cls.get_all()))

    @classmethod
    def reset_all(cls):
        for mgr in cls.get_all():
            mgr.reset()


class CTXResourceManager(MyBase, Generic[AbstractAsyncResourceT], ABC):
    """
    基于上下文管理的异步资源管理基类，适配连接池、数据库、redis等。

    支持资源字典、上下文变量托管（每协程独立资源）、成功/失败钩子、
    异常包装、事务等功能，可通过装饰器@use统一包装所有异步方法。
    """

    def __init__(
        self,
        *,
        resources: Dict[str, AbstractAsyncResourceT],
        ctx_key: CTXKey,
        success: Optional[Callable[..., Any]] = None,
        fail: Optional[Callable[..., Any]] = None,
        error: Optional[Type[SysError]] = None,
        **kwargs,
    ):
        self._ctx_key: CTXKey = ctx_key
        self._resources = resources
        self._success = success
        self._fail = fail
        self._error = error if error else SysError
        ResourceManagerRegistry.register(self)
        super().__init__(**kwargs)

        logger.info("Initialized {name}.", name=self.name)

    def __str__(self) -> str:
        return self.name

    def _check_key(self, key):
        if key not in self._resources:
            raise LibraryUsageError(f"{self.name} require {key} in config.yaml.")

    def _build_wrapper(self, func, key, use_transaction: bool = False):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            self._check_key(key)
            resource = self._resources[key]
            async with resource.db(use_transaction=use_transaction) as session:
                with CTXVarManager.use(self._ctx_key, session):
                    try:
                        result = await func(*args, **kwargs)
                        await call_hook(self._success, session)
                        return result
                    except BaseError as e:
                        raise e
                    except Exception as e:
                        logger.exception(f"{self.name} fail")
                        await call_hook(self._fail, session)
                        raise self._error(f"{self.name} fail: {e}") from None

        return wrapper

    @overload
    def use(
        self, arg: None = ..., *, use_transaction: bool = False
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...
    @overload
    def use(
        self, arg: str, *, use_transaction: bool = False
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...
    @overload
    def use(
        self, arg: Callable[..., Awaitable[Any]], *, use_transaction: bool = False
    ) -> Callable[..., Awaitable[Any]]: ...

    def use(
        self,
        arg: Optional[Union[str, Callable[..., Awaitable[Any]]]] = None,
        *,
        use_transaction: bool = False,
    ) -> Any:
        """
        主入口装饰器，用于业务异步方法
        支持三种用法：
        - @mgr.use（默认组）
        - @mgr.use('key')（指定组）
        - @mgr.use(use_transaction=True)（事务模式）
        """
        # 支持 @mgr.use
        if callable(arg):
            func = arg
            key = ConfKey.GROUP_DEFAULT
            return self._build_wrapper(func, key, use_transaction=use_transaction)

        # 支持 @mgr.use() 或 @mgr.use('key')
        def decorator(
            func: Callable[..., Awaitable[Any]],
        ) -> Callable[..., Awaitable[Any]]:
            key = arg if isinstance(arg, str) and arg else ConfKey.GROUP_DEFAULT
            return self._build_wrapper(func, key, use_transaction=use_transaction)

        return decorator

    @property
    def curr(self):
        """
        当前资源实例（仅在@use包裹等托管下调用），否则抛出异常
        """
        try:
            return CTXVarManager.get(self._ctx_key)
        except LibraryUsageError:
            raise LibraryUsageError(f"Must call {self.name}.use(...) first.") from None

    def client(self, key: str = ConfKey.GROUP_DEFAULT) -> AbstractAsyncResourceT:
        """
        按分组名获取原生底层资源实例（绕开上下文）。常用于特殊操作。
        """
        self._check_key(key)
        return self._resources[key]

    async def close(self):
        """
        关闭所有已注册资源。
        """
        for key, cli in self._resources.items():
            try:
                await cli.close()
            except:  # noqa
                logger.exception(f"{self.name} Failed to close {self} {key}")

    async def health_check(self) -> Dict[str, bool]:
        """
        批量健康检查，返回所有资源状态。
        """
        result = {}
        for key, cli in self._resources.items():
            result[key] = await cli.ping()
        return result

    def reset(self):
        """
        重置资源清单，测试/全局重启用。
        """
        self._resources = {}
