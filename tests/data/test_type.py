import smartutils.data.type as type_mod

def test_type_module():
    class MyEnum(type_mod.ZhEnumBase):
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
    assert type_mod.LowStr("ABC") == "abc"

def test_type_edge_cases():
    class MyEnum(type_mod.ZhEnumBase):
        A = 1
        @staticmethod
        def _obj_zh_map():
            return {MyEnum.A: "甲"}
        @staticmethod
        def _zh_obj_map():
            return {"甲": MyEnum.A}
    # 未实现映射
    class BadEnum(type_mod.ZhEnumBase):
        A = 1
    try:
        BadEnum.A.zh
    except NotImplementedError:
        pass
    try:
        BadEnum.from_zh("甲")
    except NotImplementedError:
        pass
    # LowStr非字符串
    assert type_mod.LowStr("ABC") == "abc"