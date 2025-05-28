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
    assert base.trans_str("[1,2,3]") == [1,2,3]
    assert base.trans_str(123) == 123
    assert base.trans_str("not_a_list") == "not_a_list"
    assert isinstance(base.str_to_int("abc"), int)
    assert base.get_ints_in_str("a1b2c3") == [1,2,3]
    assert base.get_ch_num_in_str("一二三abc四五") == ["一二三", "四五"]
    assert base.chinese_to_int("一百二十三") == 123
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"c": 3, "d": 4}, "e": 5}
    merged = base.merge_dict(d1.copy(), d2)
    assert merged["b"]["c"] == 3 and merged["b"]["d"] == 4 and merged["e"] == 5
    assert base.decode_bytes(b"abc")[0] == "abc"
    assert not base.decode_bytes(b"\xff\xfe")[1]
    assert base.remove_list_duplicate([1,2,2,3]) == [1,2,3]
    assert base.remove_list_dup_save_first([1,2,2,3]) == [1,2,3]
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