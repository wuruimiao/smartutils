from __future__ import annotations

from typing import Dict

import pytest
from pydantic import BaseModel

from smartutils.data.type import EnumMapBase, LowStr
from smartutils.error.sys import LibraryUsageError


def test_low_str():
    assert LowStr("ABC") == "abc"


class Status(EnumMapBase):
    ENABLED = "enabled"
    DISABLED = "disabled"

    @classmethod
    def _obj_map(cls) -> Dict[Status, bool]:
        return {
            cls.ENABLED: True,
            cls.DISABLED: False,
        }


class Data(BaseModel):
    status: Status


def test_enum_map_pydantic():
    # 支持Enum序列化与反序列化
    d = Data(status=Status.ENABLED)
    assert d.status == Status.ENABLED
    # 支持从原始value反序列化
    d2 = Data(status="enabled")  # type: ignore
    assert d2.status == Status.ENABLED
    # 支持从bool取Enum及fastapi形式
    d3 = Data(status=Status.from_mapped(True))
    assert d3.status == Status.ENABLED
    # 支持dict序列化
    as_dict = d.model_dump()
    assert as_dict["status"] == Status.ENABLED
    # pydantic parse_obj支持
    d4 = Data.model_validate({"status": "disabled"})
    assert d4.status == Status.DISABLED


def test_enum_map_base_mapped():
    assert Status.ENABLED.mapped is True
    assert Status.DISABLED.mapped is False


def test_enum_map_base_from_mapped():
    assert Status.from_mapped(True) is Status.ENABLED
    assert Status.from_mapped(False) is Status.DISABLED


def test_enum_map_base_try_from_mapped():
    assert Status.try_from_mapped(True) is Status.ENABLED
    assert Status.try_from_mapped(False) is Status.DISABLED
    assert Status.try_from_mapped(None) is None


def test_enum_map_base_obj_list_and_mapped_list():
    assert set(Status.obj_list()) == {Status.ENABLED, Status.DISABLED}
    assert set(Status.mapped_list()) == {True, False}


def test_enum_map_base_from_any():
    assert Status.from_any(Status.ENABLED) is Status.ENABLED
    assert Status.from_any(True) is Status.ENABLED
    with pytest.raises(ValueError):
        Status.from_any("not-exist-value")


def test_enum_map_mapped_dict_str():
    assert Status.mapped_dict_str() == "enabled: True, disabled: False"


def test_enum_mapped_dict():
    assert Status.mapped_dict() == {
        Status.ENABLED: True,
        Status.DISABLED: False,
    }


def test_enum_map_not_imp():
    class Status2(EnumMapBase):
        ENABLED = "enabled"
        DISABLED = "disabled"

    with pytest.raises(LibraryUsageError) as e:
        Status2.ENABLED.mapped
    assert str(e.value) == "Subclasses must implement _obj_map."


def test_enum_map_from_mapped_fuzzy():
    class Status1(EnumMapBase):
        ENABLED = True
        DISABLED = False

        @classmethod
        def _obj_map(cls) -> Dict[Status1, str]:
            return {
                cls.ENABLED: "enable",
                cls.DISABLED: "disable",
            }

    assert Status1.from_mapped_fuzzy("enable") == Status1.ENABLED
    assert Status1.from_mapped_fuzzy("e") is None
