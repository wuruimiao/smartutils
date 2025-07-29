import threading
from abc import ABCMeta
from functools import wraps
from typing import Callable, Dict

"""
此单例不可直接/间接在构造中做异步IO或 await 操作。
"""


__all__ = ["singleton", "SingletonBase", "SingletonMeta", "reset_all"]


class _SingleTonData:
    REGISTRY = {}
    LOCKS: Dict[type, threading.Lock] = {}
    LOCKS_LOCK = threading.Lock()

    @classmethod
    def get_instance(cls, instance_cls: type, new_instance: Callable):
        if instance_cls not in cls.LOCKS:
            with cls.LOCKS_LOCK:
                if instance_cls not in cls.LOCKS:
                    cls.LOCKS[instance_cls] = threading.Lock()

        if instance_cls not in cls.REGISTRY:
            with cls.LOCKS[instance_cls]:
                if instance_cls not in cls.REGISTRY:
                    cls.REGISTRY[instance_cls] = new_instance()

        return cls.REGISTRY[instance_cls]

    @classmethod
    def reset(cls, instance_cls: type):
        if instance_cls in cls.LOCKS:
            with cls.LOCKS[instance_cls]:
                if instance_cls in cls.REGISTRY:
                    cls.REGISTRY.pop(instance_cls)

    @classmethod
    def reset_all(cls):
        for instance_cls in cls.LOCKS.keys():
            cls.reset(instance_cls)


def singleton(cls):
    """
    单例装饰器，支持reset
    使用方式：
    @singleton
    class MyClass: ...
    """
    # 未拦截__init__，每次调用实例化都会执行一次__init__
    # class _SingletonWrapper(cls):
    #     _instance = None
    #     _lock = threading.Lock()

    #     def __new__(cls, *args, **kwargs):
    #         if cls._instance is None:
    #             with cls._lock:
    #                 if cls._instance is None:
    #                     # 兼容父类 __new__ 是否支持参数
    #                     try:
    #                         cls._instance = super(_SingletonWrapper, cls).__new__(
    #                             cls, *args, **kwargs
    #                         )
    #                     except TypeError:
    #                         cls._instance = super(_SingletonWrapper, cls).__new__(cls)
    #         return cls._instance

    # _SingletonWrapper.__name__ = cls.__name__
    # _SingletonWrapper.__doc__ = cls.__doc__
    # return _SingletonWrapper

    # 用 class 装饰器返回了实例（不是类），破坏了类方法的运行机制
    @wraps(cls)
    def get_instance(*args, **kwargs):
        return _SingleTonData.get_instance(cls, lambda: cls(*args, **kwargs))

    def reset():
        _SingleTonData.reset(cls)

    get_instance.reset = reset  # type: ignore
    return get_instance


class SingletonMeta(ABCMeta):
    """
    单例元类，支持reset和reset_all
    class MyMetaSingleton(metaclass=SingletonMeta): ...
    """

    def __call__(cls, *args, **kwargs):
        return _SingleTonData.get_instance(
            cls, lambda: super(SingletonMeta, cls).__call__(*args, **kwargs)
        )

    def reset(cls):
        _SingleTonData.reset(cls)


class SingletonBase(metaclass=SingletonMeta):
    """
    单例基类。支持reset和reset_all
    使用方式：
    class MySingleton(SingletonBase): ...
    """

    # def __new__(cls, *args, **kwargs):
    #     return _SingleTonData.get_instance(
    #         cls, lambda: super(SingletonBase, cls).__new__(cls, *args, **kwargs)
    #     )

    def _init_once(self, *args, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        if getattr(self, "_initialized", False):
            return  # pragma: no cover
        self._init_once(*args, **kwargs)
        self._initialized = True

    @classmethod
    def reset(cls):
        _SingleTonData.reset(cls)


def reset_all():
    # 全部清空
    _SingleTonData.reset_all()
