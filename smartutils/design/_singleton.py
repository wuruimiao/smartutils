import threading
from functools import wraps

"""
此单例不可直接/间接在构造中做异步IO或 await 操作。
"""


__all__ = ["singleton", "SingletonBase", "SingletonMeta", "reset_all"]

_singleton_instances = {}
_singleton_lock = threading.Lock()


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
        if cls not in _singleton_instances:
            with _singleton_lock:
                if cls not in _singleton_instances:
                    _singleton_instances[cls] = cls(*args, **kwargs)
        return _singleton_instances[cls]

    def reset():
        with _singleton_lock:
            _singleton_instances.pop(cls, None)

    get_instance.reset = reset  # type: ignore
    return get_instance


class SingletonBase:
    """
    单例基类。支持reset和reset_all
    使用方式：
    class MySingleton(SingletonBase): ...
    """

    _instance = None
    _lock = threading.Lock()
    _singleton_classes = set()

    def __new__(cls, *args, **kwargs):
        # 注册到单例集合
        if cls is not SingletonBase:
            SingletonBase._singleton_classes.add(cls)
        if not hasattr(cls, "_instance") or cls._instance is None:
            with cls._lock:
                if not hasattr(cls, "_instance") or cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _init_once(self, *args, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        if getattr(self, "_initialized", False):
            return
        self._init_once(*args, **kwargs)
        self._initialized = True

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None

    @classmethod
    def reset_all(cls):
        """
        重置所有继承自 SingletonBase 的单例实例
        """
        for sub_cls in list(cls._singleton_classes):
            sub_cls.reset()


class SingletonMeta(type):
    """
    单例元类，支持reset和reset_all
    class MyMetaSingleton(metaclass=SingletonMeta): ...
    """

    _instances = {}
    _locks = {}
    _locks_control = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._locks:
            with SingletonMeta._locks_control:
                if cls not in SingletonMeta._locks:
                    SingletonMeta._locks[cls] = threading.Lock()
        # 后续的加锁只用自己 class 的锁
        if cls not in SingletonMeta._instances:
            with SingletonMeta._locks[cls]:
                if cls not in SingletonMeta._instances:
                    SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

    def reset(cls):
        if cls in SingletonMeta._locks:
            with SingletonMeta._locks[cls]:
                SingletonMeta._instances.pop(cls, None)

    @classmethod
    def reset_all(mcs):
        for cls in list(mcs._instances):
            if cls in mcs._locks:
                with mcs._locks[cls]:
                    mcs._instances.pop(cls, None)


def reset_all():
    with _singleton_lock:
        _singleton_instances.clear()
    SingletonBase.reset_all()
    SingletonMeta.reset_all()
