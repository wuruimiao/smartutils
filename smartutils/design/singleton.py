import threading
from functools import wraps


def singleton(cls):
    """
    单例装饰器
    重置使用方式
    @singleton
    class MyClass: ...
    MyClass.reset()
    """
    instances = {}
    lock = threading.Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    def reset():
        """
        重置当前类
        """
        with lock:
            instances.pop(cls, None)

    get_instance.reset = reset
    return get_instance


class SingletonBase:
    """
    单例基类
    重置使用方式:
    class MySingleton(SingletonBase): ...
    MySingleton.reset()
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or cls._instance is None:
            with cls._lock:
                if not hasattr(cls, '_instance') or cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _init_once(self, *args, **kwargs):
        pass

    def __init__(self, *args, **kwargs):
        if getattr(self, '_initialized', False):
            return
        self._init_once(*args, **kwargs)
        self._initialized = True

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None


class SingletonMeta(type):
    """
    单例元类
    使用方式:
    class MyMetaSingleton(metaclass=SingletonMeta): ...
    MyMetaSingleton.reset()
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def reset(cls):
        with SingletonMeta._lock:
            SingletonMeta._instances.pop(cls, None)
