import os
import sys
import tempfile

import pytest

from smartutils.file import _filename


def test_file_name_and_base_ext():
    path = "/home/user/test.data.txt"
    assert _filename.file_name(path) == "test.data.txt"
    # os.path.splitext分割只去掉最后一段后缀
    base, ext = _filename.filename_base_ext(path)
    assert base == "test.data"
    assert ext == "txt"


def test_filename_other_format_and_add_num():
    assert _filename.filename_other_format("abc.json", "yml") == "abc.yml"
    assert _filename.filename_other_format("file.conf", "") == "file"
    assert _filename.filename_add_num("abc.txt", 5) == "abc5.txt"
    # 没有扩展名
    assert _filename.filename_add_num("naked", 7) == "naked7"


def test_is_remote_path_variants():
    assert _filename.is_remote_path(r"\\nas\foo") is True
    assert _filename.is_remote_path(r"C:\\xx\\bar") is False
    assert _filename.is_remote_path("/usr/bin") is False


def test_buff_size_and_get_name_with_i():
    assert isinstance(_filename.buff_size(), int) and _filename.buff_size() > 1000
    assert _filename.get_name_with_i("foo.txt", 0) == "foo.txt"
    assert _filename.get_name_with_i("foo.txt", 3) == "foo3.txt"


def test_format_file_name_multi_version():
    # version=1 保持原样
    whatever = r't e|s/t\【】【】.t|s,"?.q'
    assert _filename.format_file_name(whatever, version=1) == whatever
    # version=2 基本去除管道与斜杠
    v2 = _filename.format_file_name(whatever, version=2)
    assert "|" not in v2 and "/" not in v2 and "\\" not in v2
    # version=3/4/5 进一步去除特殊标点空格并下划线替换
    v5 = _filename.format_file_name(whatever, version=5)
    assert " " not in v5
    assert all(c not in v5 for c in '|/\\?.,"[]【】')


def test_sanitize_filename_linux_windows():
    # 同时替换所有非法字符
    origin = 'test<>:"/\\|?*%. '
    sanitized = _filename.sanitize_filename(origin, linux=True, windows=True)
    assert sanitized.endswith("_")
    assert all(c not in sanitized for c in '<>:"/\\|?*%.')


def test_check_file_exist_and_is_really_file(tmp_path):
    f = tmp_path / "some.file"
    f.write_text("abc", encoding="utf-8")
    assert _filename.check_file_exist(str(f))
    assert _filename.is_really_file(str(f))
    # 目录不是文件
    assert not _filename.check_file_exist(str(tmp_path))
    # 虚拟路径带.但没建应为False
    assert not _filename.check_file_exist(str(tmp_path / "non.exist"))


def test_is_link_and_link_target(tmp_path):
    f = tmp_path / "origin.txt"
    f.write_text("ok", encoding="utf-8")
    link = tmp_path / "sym"
    os.symlink(f, link)
    assert _filename.is_link(str(link))
    assert _filename.link_target(str(link)) == str(f.resolve())
    # 普通文件不是链接
    assert not _filename.is_link(str(f))


def test_dir_listing_utils(tmp_path):
    # 构造嵌套目录和文件结构
    d1 = tmp_path / "d1"
    d2 = d1 / "d2"
    d2.mkdir(parents=True)
    f1 = d1 / "a.txt"
    f2 = d2 / "b.txt"
    f1.write_text("f1", encoding="utf-8")
    f2.write_text("f2", encoding="utf-8")

    # my_listdir递归收集
    L = []
    _filename.my_listdir(str(tmp_path), L)
    assert str(f1) in L and str(f2) in L

    # deep_list_dir_files
    all_files = _filename.deep_list_dir_files(str(tmp_path))
    assert set(L) == set(all_files)

    # paths_in_path/dirs_in_dir
    all_dirs = _filename.paths_in_path(str(tmp_path))
    assert str(d1.name) in all_dirs
    assert d1.name in all_dirs  # path(str) 和 name
    # full_paths_in_path只返回目录绝对路径
    full_dirs = _filename.full_paths_in_path(str(tmp_path))
    assert any(str(d1) in d for d in full_dirs)

    # all_fs_in_dir
    assert d1.name in _filename.all_fs_in_dir(str(tmp_path))
    # filepath_in_dir / filename_in_dir
    fset = _filename.filepath_in_dir(str(d1))
    nset = _filename.filename_in_dir(str(d1))
    assert str(f1) in fset
    assert f1.name in nset


def test_dirs_in_dir_is_paths_in_path_equivalent(tmp_path):
    d = tmp_path / "dirA"
    d.mkdir()
    assert _filename.dirs_in_dir(str(tmp_path)) == _filename.paths_in_path(
        str(tmp_path)
    )
