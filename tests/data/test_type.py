import pytest

from smartutils.data.type import LowStr, ZhEnumBase


def test_type_module():
    class MyEnum(ZhEnumBase):
        A = 1
        B = 2

        @staticmethod
        def _obj_zh_map():
            return {MyEnum.A: "甲", MyEnum.B: "乙"}

        @staticmethod
        def _zh_obj_map():
            return {"甲": MyEnum.A, "乙": MyEnum.B}

    assert MyEnum.A.zh == "甲"
    assert MyEnum.from_zh("乙") == MyEnum.B
    assert MyEnum.zh_from_value(1) == "甲"
    assert MyEnum.value_from_zh("乙") == 2
    assert (MyEnum.A, "甲") in MyEnum.zh_choices()
    assert "1: 甲" in MyEnum.zh_choices_str()
    assert "甲" in MyEnum.zh_list()
    assert LowStr("ABC") == "abc"


def test_type_edge_cases():
    class MyEnum(ZhEnumBase):
        A = 1

        @staticmethod
        def _obj_zh_map():
            return {MyEnum.A: "甲"}

        @staticmethod
        def _zh_obj_map():
            return {"甲": MyEnum.A}

    class BadEnum(ZhEnumBase):
        A = 1

    try:
        BadEnum.A.zh
    except NotImplementedError:
        pass
    try:
        BadEnum.from_zh("甲")
    except NotImplementedError:
        pass
    assert LowStr("ABC") == "abc"


def test_obj_zh_map_not_implemented():
    class MyEnum(ZhEnumBase):
        A = 1

    with pytest.raises(NotImplementedError):
        MyEnum._obj_zh_map()


def test_zh_obj_map_not_implemented():
    class MyEnum(ZhEnumBase):
        A = 1

    with pytest.raises(NotImplementedError):
        MyEnum._zh_obj_map()
