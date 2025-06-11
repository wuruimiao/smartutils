import os

import pytest

from smartutils.file import _path


def test_norm_path_basic_cases():
    # 相对、绝对路径、去重斜杠、对.././去冗余
    assert _path.norm_path("foo//bar/../baz") == os.path.normpath("foo/bar/../baz")
    assert _path.norm_path("C:\\\\data//x") == os.path.normpath(r"C:\\data/x")
    # 空或.情况
    assert _path.norm_path("") == os.path.normpath("")
    assert _path.norm_path(".") == os.path.normpath(".")


def test_check_path_exist_and_real(tmp_path):
    d = tmp_path / "a"
    d.mkdir()
    f = d / "b.txt"
    f.write_text("hi")
    assert _path.check_path_exist(str(d))
    assert _path.check_path_exist(str(f))
    nf = tmp_path / "none.txt"
    assert not _path.check_path_exist(str(nf))


def test_get_file_path_and_parts(tmp_path):
    base = tmp_path / "some"
    base.mkdir()
    f = _path.get_file_path(str(base), "x.txt")
    assert f.endswith("x.txt")
    f2 = _path.get_file_path(str(base), "")
    assert isinstance(f2, str)
