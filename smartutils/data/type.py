from enum import Enum
from typing import TypeVar, Type, Any, Dict

__all__ = ["ZhEnumBase", "LowStr"]


T = TypeVar("T", bound="ZhEnumBase")


class ZhEnumBase(Enum):
    """
    支持变量-中文双向映射的通用枚举基类。
    子类不要在类体里写映射字典，需在类外写。
    """

    @property
    def zh(self) -> str:
        return self._obj_zh_map()[self]

    @classmethod
    def from_zh(cls: Type[T], zh: str) -> T:
        return cls._zh_obj_map()[zh]

    @classmethod
    def zh_from_value(cls: Type[T], value: Any) -> str:
        return cls(value).zh

    @classmethod
    def value_from_zh(cls: Type[T], zh: str) -> Any:
        return cls.from_zh(zh).value

    @classmethod
    def zh_choices(cls: Type[T]):
        return [(e, e.zh) for e in cls]

    @classmethod
    def zh_choices_str(cls) -> str:
        return " ".join(f"{item.value}: {item.zh}" for item in cls)

    @classmethod
    def zh_list(cls: Type[T]):
        return [e.zh for e in cls]

    @staticmethod
    def _obj_zh_map() -> Dict[Any, str]:
        raise NotImplementedError("子类必须实现 _obj_zh_map 方法")

    @staticmethod
    def _zh_obj_map() -> Dict[str, Any]:
        raise NotImplementedError("子类必须实现 _zh_obj_map 方法")


class LowStr(str):
    def __new__(cls, s: str):
        return str.__new__(cls, s.lower())
