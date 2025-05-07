from typing import Optional, Dict, Type, Tuple, Callable

from smartutils.ID.abstract import AbstractIDGenerator
from smartutils.ID.const import IDGenType


class _IDGen(AbstractIDGenerator):
    def __init__(self):
        self._gen: Optional[AbstractIDGenerator] = None
        self._type: Optional[IDGenType] = None
        self._registry: Dict[IDGenType, Tuple[Callable[..., AbstractIDGenerator], bool]] = {}

    def register(self, id_type: IDGenType, need_conf: bool = False):
        def decorator(gen_cls: Type[AbstractIDGenerator]) -> Type[AbstractIDGenerator]:
            self._registry[id_type] = (gen_cls, need_conf)
            return gen_cls

        return decorator

    def init(self, id_gen_type: IDGenType = IDGenType.ULID, conf=None):
        if id_gen_type not in self._registry:
            raise ValueError(f"IDGen {id_gen_type} not registered")
        self._type = id_gen_type
        gen_cls, need_conf = self._registry[id_gen_type]
        if need_conf:
            if not conf:
                raise ValueError(f"IDGen {gen_cls} need conf")
            self._gen = gen_cls(**conf.kw)
        else:
            self._gen = gen_cls()

    def __next__(self):
        if self._gen is None:
            raise RuntimeError("IDGen need init, call IDGen.init(...) first")
        return self._gen()

    def __repr__(self):
        return f"<IDGen(type={self._type})>"


IDGen = _IDGen()

__all__ = ["IDGen", "IDGenType"]
