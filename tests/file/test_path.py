import os
import tempfile

from smartutils.file import _path


def test_norm_path_and_exist(tmp_path):
    p = tmp_path / "abc"
    normed = _path.norm_path(str(p))
    assert os.path.isabs(normed)
    # 存在性检测
    assert not _path.check_path_exist(str(p))
    p.mkdir()
    assert _path.check_path_exist(str(p))


def test_get_path_last_part():
    assert _path.get_path_last_part("/tmp/xx/abc.txt") == "abc.txt"
    assert _path.get_path_last_part("a/b/c/") == ""


def test_get_file_path():
    # 单一拼接
    base = "/tmp/aaa"
    assert _path.get_file_path(base, "b.txt") == os.path.join(base, "b.txt")
    # 多参数拼接
    out = _path.get_file_path("/a", "b", "c.txt")
    assert out.endswith("b/c.txt")


def test_real_and_abspath(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("a")
    abspath = _path.abs_path(str(f))
    assert os.path.exists(abspath)
    real = os.path.realpath(str(f))  # -- 用 os.path.realpath 兼容实现
    assert os.path.exists(real)
