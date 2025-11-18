import dataclasses

import pytest

import smartutils.data.dict
import smartutils.data.int
import smartutils.data.list
import smartutils.data.str
import smartutils.data.tree
from smartutils.error.sys import LibraryUsageError


def test_data_int():
    assert smartutils.data.int.max_int() > 0
    assert smartutils.data.int.min_int() < 0
    assert smartutils.data.int.max_float() > 0
    assert smartutils.data.int.min_float() < 0
    assert smartutils.data.int.max_int() == 9223372036854775807
    assert smartutils.data.int.min_int() == -9223372036854775807
    assert smartutils.data.int.max_float() == 1.7976931348623157e308
    assert smartutils.data.int.min_float() == -1.7976931348623157e308

    assert smartutils.data.int.is_num(123)
    assert smartutils.data.int.is_num(1.23)
    assert smartutils.data.int.is_num("123")
    assert smartutils.data.int.is_num("1.23")
    assert not smartutils.data.int.is_num("abc")
    # is_num 负数和小数点情况
    assert not smartutils.data.int.is_num("-123")
    assert not smartutils.data.int.is_num("1..23")
    # float 类型直接 True
    assert smartutils.data.int.is_num(1.23)
    # str 多个点、其他特殊字符
    assert not smartutils.data.int.is_num("12.3.4")


def test_data_str():
    assert smartutils.data.str.md5("abc") == smartutils.data.str.md5("abc")
    assert smartutils.data.str.trans_str("[1,2,3]") == [1, 2, 3]
    assert smartutils.data.str.trans_str(123) == 123  # type: ignore
    assert smartutils.data.str.trans_str("not_a_list") == "not_a_list"
    assert isinstance(smartutils.data.str.str_to_int("abc"), int)
    assert smartutils.data.str.get_ints_in_str("a1b2c3") == [1, 2, 3]
    assert smartutils.data.str.get_ch_num_in_str("一二三abc四五") == ["一二三", "四五"]
    assert smartutils.data.str.chinese_to_int("一百二十三") == 123


def test_base_edge_cases():
    # is_num
    assert not smartutils.data.int.is_num(None)
    assert not smartutils.data.int.is_num("")
    assert not smartutils.data.int.is_num("abc")
    assert smartutils.data.int.is_num("1.23")
    assert not smartutils.data.int.is_num("-1.23")  # 负号不被原实现识别
    # trans_str
    assert smartutils.data.str.trans_str("{a:1}") == "{a:1}"
    assert smartutils.data.str.trans_str("") == ""
    # merge_dict path参数
    a = {"a": {"b": 1}}
    b = {"a": {"b": 2}}
    smartutils.data.dict.merge_dict(a, b, path=["a"])
    # decode_bytes空
    assert smartutils.data.dict.decode_bytes(b"") == ("", True)
    # remove_list_duplicate空
    assert smartutils.data.list.remove_duplicate([]) == []
    # remove_list_dup_save_first空
    assert smartutils.data.list.remove_duplicate([], save_first=True) == []

    # make_parent孤儿
    class Info:
        def __init__(self, id, parent_id=0):
            self.id = id
            self.parent_id = parent_id
            self.children = []

    data = [dict(id=1, parent_id=2), dict(id=2, parent_id=0)]
    tree = smartutils.data.tree.make_parent(data, Info)
    assert 2 in tree
    # make_children无parent
    children = smartutils.data.tree.make_children([dict(id=1, parent_id=0)], Info)
    assert 1 in children


def test_data_dict_to_json():
    d = {"b": 2, "a": 1}
    assert smartutils.data.dict.to_json(d, sort=True) == b'{"a":1,"b":2}'
    assert smartutils.data.dict.to_json(d, sort=False) == b'{"b":2,"a":1}'
    assert (
        smartutils.data.dict.to_json(d, sort=True, indent_2=True)
        == b'{\n  "a": 1,\n  "b": 2\n}'
    )
    assert smartutils.data.dict.to_json({1: 2, 3: 4}) == b'{"1":2,"3":4}'


def test_data_dict():
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"c": 3, "d": 4}, "e": 5}
    merged = smartutils.data.dict.merge_dict(d1.copy(), d2)
    assert merged["b"]["c"] == 3 and merged["b"]["d"] == 4 and merged["e"] == 5
    assert smartutils.data.dict.decode_bytes(b"abc")[0] == "abc"
    assert not smartutils.data.dict.decode_bytes(b"\xff\xfe")[1]


def test_data_list():
    assert smartutils.data.list.remove_duplicate([1, 2, 2, 3]) == [1, 2, 3]
    assert smartutils.data.list.remove_duplicate([1, 2, 2, 3], save_first=True) == [
        1,
        2,
        3,
    ]


def test_data_dict_to_json_auto_trans():
    # dataclass可以直接序列化，不用asdict
    @dataclasses.dataclass
    class SampleData:
        id: int
        name: str

    data = SampleData(id=1, name="test")
    json_bytes = smartutils.data.dict.to_json(dataclasses.asdict(data))
    assert json_bytes == b'{"id":1,"name":"test"}'

    # class不能直接序列化，会报错
    class SampleData2:
        def __init__(self, id: int, name: str):
            self.id = id
            self.name = name

    data2 = SampleData2(id=2, name="demo")
    with pytest.raises(TypeError) as exec:
        smartutils.data.dict.to_json(data2)
    assert "Type is not JSON serializable: SampleData2" in str(exec.value)

    # uuid自动转换
    import uuid

    uid = uuid.uuid4()
    assert smartutils.data.dict.to_json({"uid": uid}) == f'{{"uid":"{uid}"}}'.encode()

    # 测试default参数
    @dataclasses.dataclass
    class CustomData:
        id: int
        name: str

        def to_json(self):
            return {"id": self.id}

    val = smartutils.data.dict.to_json(
        CustomData(1, "test"), trans_dataclass=lambda x: x.to_json()
    )
    assert val == b'{"id":1}'


def test_data_Encodable():
    @dataclasses.dataclass
    class SampleData(smartutils.data.dict.Encodable):
        id: int
        name: str

    data = SampleData(id=1, name="test")
    encoded = data.encode()
    assert encoded == b'{"id":1,"name":"test"}'
    decoded = SampleData.decode(encoded)
    assert decoded.id == data.id and decoded.name == data.name
    decoded = SampleData.decode(encoded.decode())
    assert decoded.id == data.id and decoded.name == data.name

    # 测试非dataclass子类
    class SampleData2(smartutils.data.dict.Encodable):
        def __init__(self, id: int, name: str):
            self.id = id
            self.name = name

    data = SampleData2(id=2, name="demo")
    with pytest.raises(LibraryUsageError) as exec:
        data.encode()
    assert "Subclasses of Encodable must be dataclasses." == str(exec.value)


def test_merge_dict_edge():

    # 嵌套 dict + 非 dict 冲突
    a = {"a": {"b": 1}, "c": 2}
    b = {"a": 3, "d": 4}
    merged = smartutils.data.dict.merge_dict(a.copy(), b)
    assert merged["a"] == 3
    assert merged["d"] == 4  # 原错误assert为5（应为4）
    # 纯嵌套 dict 合并
    a = {"a": {"b": 1}}
    b = {"a": {"c": 2}}
    merged = smartutils.data.dict.merge_dict(a.copy(), b)
    assert merged["a"]["b"] == 1 and merged["a"]["c"] == 2


def test_detect_cycle_real_cycle():
    # 构造一个有环的 id_to_parent
    id_to_parent = {1: 2, 2: 3, 3: 1}
    has_cycle, clean_map = smartutils.data.tree.detect_cycle(id_to_parent)
    assert has_cycle is True
    assert any(v == 0 for v in clean_map.values())

    # make_parent/make_children 自动剔环
    class Info:
        def __init__(self, id, parent_id=0):
            self.id = id
            self.parent_id = parent_id
            self.children = []

    data = [dict(id=1, parent_id=2), dict(id=2, parent_id=3), dict(id=3, parent_id=1)]
    tree = smartutils.data.tree.make_parent(data, Info)
    assert any(x in tree for x in [1, 2, 3])
    children = smartutils.data.tree.make_children(data, Info)
    assert set(children.keys()) == {1, 2, 3}
    for v in children.values():
        assert len(v) >= 1


def test_data_tree():
    class Info:
        def __init__(self, id, parent_id=0):
            self.id = id
            self.parent_id = parent_id
            self.children = []

    data = [dict(id=1, parent_id=0), dict(id=2, parent_id=1)]
    val = smartutils.data.tree.make_parent(data, Info)
    assert 1 in val and val[1].children[0].id == 2
    children = smartutils.data.tree.make_children(data, Info)
    assert 2 in children and children[2][0].id == 1
