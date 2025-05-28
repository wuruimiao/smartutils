import smartutils.data.csv as csv_mod
import tempfile
import os

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
    assert rows2[0]["a"] == "1"
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
        pass