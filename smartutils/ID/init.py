from typing import Optional, Dict, Type

from smartutils.ID.abstract import AbstractIDGenerator
from smartutils.ID.const import IDGenType


class _IDGen(AbstractIDGenerator):
    def __init__(self):
        self._gen: Optional[AbstractIDGenerator] = None
        self._type: Optional[IDGenType] = None
        self._registry: Dict[IDGenType, Type[AbstractIDGenerator]] = {}

    def register(self, id_type: IDGenType):
        def decorator(gen_cls: Type[AbstractIDGenerator]) -> Type[AbstractIDGenerator]:
            self._registry[id_type] = gen_cls
            return gen_cls

        return decorator

    def init(self, id_gen_type: IDGenType = IDGenType.ULID, **kwargs):
        if id_gen_type not in self._registry:
            raise ValueError(f"IDGen {id_gen_type} not registered")
        self._type = id_gen_type
        self._gen = self._registry[id_gen_type](**kwargs)

    def __next__(self):
        if self._gen is None:
            raise RuntimeError("IDGen need init, call IDGen.init(...) first")
        return self._gen()

    def __repr__(self):
        return f"<IDGen(type={self._type})>"


IDGen = _IDGen()

__all__ = ["IDGen", "IDGenType"]
