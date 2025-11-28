import sys
from abc import ABC, abstractmethod

if sys.version_info >= (3, 11):
    from typing import override
else:
    from typing_extensions import override

__all__ = ["AbstractIDGenerator"]


class AbstractIDGenerator(ABC):
    @abstractmethod
    def __next__(self):
        """
        获取下一个ID
        """
        ...

    def __iter__(self):
        """
        让生成器对象可用于 for 循环等迭代场景
        """
        return self

    def __call__(self):
        """
        使实例可直接调用生成ID
        """
        return next(self)

    @abstractmethod
    @override
    def __repr__(self) -> str: ...
