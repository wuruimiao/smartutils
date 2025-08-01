import os
import tempfile

import smartutils.data.csv as csv_mod


def test_csv_module():
    # 创建临时csv文件
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("a,b\n1,2\n3,4\n")
        fname = f.name
    called = []

    def handler(line):
        called.append(line)
        return True

    csv_mod.csv_to_data(fname, handler)
    assert len(called) == 2
    rows = list(csv_mod.csv_data(fname))
    assert rows[0]["a"] == "1"
    assert rows[1]["b"] == "4"
    rows2 = csv_mod.get_csv_data(fname)
    assert rows2[0]["a"] == "1"  # type: ignore
    csv_mod.increase_csv_limit()  # 只需覆盖
    os.remove(fname)


def test_csv_edge_cases():
    # 空文件
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        fname = f.name
    rows = list(csv_mod.csv_data(fname))
    assert rows == []
    os.remove(fname)
    # handler返回False
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("a,b\n1,2\n3,4\n")
        fname = f.name
    called = []

    def handler(line):
        called.append(line)
        return False

    csv_mod.csv_to_data(fname, handler)
    assert len(called) == 1
    os.remove(fname)
    # 异常路径
    try:
        list(csv_mod.csv_data("not_exist.csv"))
    except Exception:
        ...


def test_increase_csv_limit_overflow(mocker):
    # 模拟 csv.field_size_limit 抛出 OverflowError 一次，然后成功
    import smartutils.data.csv as csv_mod

    called = {"count": 0}

    def fake_limit(val):
        if called["count"] == 0:
            called["count"] += 1
            raise OverflowError
        return 123

    mocker.patch.object(csv_mod.csv, "field_size_limit", fake_limit)
    csv_mod.increase_csv_limit()
