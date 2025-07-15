import smartutils.data.base as base


def test_base_module():
    assert base.max_int() > 0
    assert base.min_int() < 0
    assert base.is_num(123)
    assert base.is_num(1.23)
    assert base.is_num("123")
    assert base.is_num("1.23")
    assert not base.is_num("abc")
    assert base.md5("abc") == base.md5("abc")
    assert base.trans_str("[1,2,3]") == [1, 2, 3]
    assert base.trans_str(123) == 123  # type: ignore
    assert base.trans_str("not_a_list") == "not_a_list"
    assert isinstance(base.str_to_int("abc"), int)
    assert base.get_ints_in_str("a1b2c3") == [1, 2, 3]
    assert base.get_ch_num_in_str("一二三abc四五") == ["一二三", "四五"]
    assert base.chinese_to_int("一百二十三") == 123
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"c": 3, "d": 4}, "e": 5}
    merged = base.merge_dict(d1.copy(), d2)
    assert merged["b"]["c"] == 3 and merged["b"]["d"] == 4 and merged["e"] == 5
    assert base.decode_bytes(b"abc")[0] == "abc"
    assert not base.decode_bytes(b"\xff\xfe")[1]
    assert base.remove_list_duplicate([1, 2, 2, 3]) == [1, 2, 3]
    assert base.remove_list_dup_save_first([1, 2, 2, 3]) == [1, 2, 3]

    class Info:
        def __init__(self, id, parent_id=0):
            self.id = id
            self.parent_id = parent_id
            self.children = []

    data = [dict(id=1, parent_id=0), dict(id=2, parent_id=1)]
    tree = base.make_parent(data, Info)
    assert 1 in tree and tree[1].children[0].id == 2
    children = base.make_children(data, Info)
    assert 2 in children and children[2][0].id == 1


def test_base_edge_cases():
    # is_num
    assert not base.is_num(None)
    assert not base.is_num("")
    assert not base.is_num("abc")
    assert base.is_num("1.23")
    assert not base.is_num("-1.23")  # 负号不被原实现识别
    # trans_str
    assert base.trans_str("{a:1}") == "{a:1}"
    assert base.trans_str("") == ""
    # merge_dict path参数
    a = {"a": {"b": 1}}
    b = {"a": {"b": 2}}
    base.merge_dict(a, b, path=["a"])
    # decode_bytes空
    assert base.decode_bytes(b"") == ("", True)
    # remove_list_duplicate空
    assert base.remove_list_duplicate([]) == []
    # remove_list_dup_save_first空
    assert base.remove_list_dup_save_first([]) == []

    # make_parent孤儿
    class Info:
        def __init__(self, id, parent_id=0):
            self.id = id
            self.parent_id = parent_id
            self.children = []

    data = [dict(id=1, parent_id=2), dict(id=2, parent_id=0)]
    tree = base.make_parent(data, Info)
    assert 1 in tree or 2 in tree
    # make_children无parent
    children = base.make_children([dict(id=1, parent_id=0)], Info)
    assert 1 in children


def test_dict_json_and_is_num():
    d = {"b": 2, "a": 1}
    assert base.dict_json(d) in ('{"b": 2, "a": 1}', '{"a": 1, "b": 2}')
    assert base.dict_json(d, sort=True) == '{"a": 1, "b": 2}'
    # is_num 负数和小数点情况
    assert not base.is_num("-123")
    assert not base.is_num("1..23")
    # float 类型直接 True
    assert base.is_num(1.23)
    # str 多个点、其他特殊字符
    assert not base.is_num("12.3.4")


def test_merge_dict_edge():
    import smartutils.data.base as base

    # 嵌套 dict + 非 dict 冲突
    a = {"a": {"b": 1}, "c": 2}
    b = {"a": 3, "d": 4}
    merged = base.merge_dict(a.copy(), b)
    assert merged["a"] == 3
    assert merged["d"] == 4  # 原错误assert为5（应为4）
    # 纯嵌套 dict 合并
    a = {"a": {"b": 1}}
    b = {"a": {"c": 2}}
    merged = base.merge_dict(a.copy(), b)
    assert merged["a"]["b"] == 1 and merged["a"]["c"] == 2


def test_detect_cycle_real_cycle():
    # 构造一个有环的 id_to_parent
    id_to_parent = {1: 2, 2: 3, 3: 1}
    has_cycle, clean_map = base.detect_cycle(id_to_parent)
    assert has_cycle is True
    assert any(v == 0 for v in clean_map.values())

    # make_parent/make_children 自动剔环
    class Info:
        def __init__(self, id, parent_id=0):
            self.id = id
            self.parent_id = parent_id
            self.children = []

    data = [dict(id=1, parent_id=2), dict(id=2, parent_id=3), dict(id=3, parent_id=1)]
    tree = base.make_parent(data, Info)
    assert any(x in tree for x in [1, 2, 3])
    children = base.make_children(data, Info)
    assert set(children.keys()) == {1, 2, 3}
    for v in children.values():
        assert len(v) >= 1
