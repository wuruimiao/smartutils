import os
import shutil
import tempfile

import pytest

from smartutils.error.sys import FileError, FileInvalidError, NoFileError
from smartutils.file import fileop


def test_load_and_dump_f(tmp_path):
    file = tmp_path / "a.txt"
    content = "hello\nworld"
    assert fileop.dump_f(str(file), content).is_ok
    s, err = fileop.load_f(str(file))
    assert s == content
    assert err.is_ok


def test_load_f_line_unknown_and_invalid(tmp_path):
    file = tmp_path / "none.txt"
    # file不存在
    lines, err = fileop.load_f_line(str(file))
    assert lines == [] and isinstance(err, NoFileError)
    # 非utf8文件内容
    bfile = tmp_path / "bad.txt"
    bfile.write_bytes(b"abc\xff\xff")
    lines, err = fileop.load_f_line(str(bfile))
    assert lines == [] and isinstance(err, FileInvalidError)


def test_dump_b_f_and_is_binary(tmp_path):
    file = tmp_path / "data.bin"
    assert fileop.dump_b_f(str(file), b"\x00\x01abc").is_ok
    assert fileop.is_binary_f(str(file))
    # 文本文件识别为非binary
    tfile = tmp_path / "t.txt"
    tfile.write_text("ascii", encoding="utf-8")
    assert not fileop.is_binary_f(str(tfile))


def test_append_and_dump_lines(tmp_path):
    file = tmp_path / "lines.txt"
    fileop.dump_f_lines(str(file), ["a", "b", 3])
    fileop.append_f_line(str(file), "c")
    fileop.append_f_lines(str(file), ["d", 5])
    with open(file, encoding="utf-8") as f:
        lines = f.readlines()
    assert "a\n" in lines and "3\n" in lines and "c\n" in lines and "5\n" in lines


def test_copy_and_move_file(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("hi", encoding="utf-8")
    dst = tmp_path / "dst.txt"
    fileop.copy_file(str(src), str(dst))
    assert dst.exists() and dst.read_text(encoding="utf-8") == "hi"
    fileop.move_file(str(dst), str(src))
    assert src.exists()


def test_rename_and_rm(tmp_path):
    src = tmp_path / "aa.txt"
    src.write_text("z", encoding="utf-8")
    dst = tmp_path / "bb.txt"
    fileop.rename_f(str(src), str(dst))
    assert dst.exists() and not src.exists()
    fileop.rm_file(str(dst))
    assert not dst.exists()


def test_copy_dir_and_move_dir(tmp_path):
    src_dir = tmp_path / "d1"
    src_dir.mkdir()
    (src_dir / "f1.txt").write_text("x")
    (src_dir / "f2.txt").write_text("y")
    dst_dir = tmp_path / "d2"
    cnt = fileop.copy_dir(str(src_dir), str(dst_dir))
    assert (dst_dir / "f2.txt").exists()
    fileop.move_dir(str(dst_dir), str(src_dir / "sub"))
    assert (src_dir / "sub" / "f1.txt").exists()


def test_file_size_sha2(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("sha-test", encoding="utf-8")
    sz = fileop.file_size(str(f))
    assert sz == len("sha-test")
    hval = fileop.sha2_file(str(f))
    assert len(hval) == 64


def test_get_f_time_and_cmp_file(tmp_path):
    f1 = tmp_path / "fa"
    f2 = tmp_path / "fb"
    txt = "x" * 4000
    f1.write_text(txt, encoding="utf-8")
    f2.write_text(txt, encoding="utf-8")
    assert fileop.cmp_file(str(f1), str(f2))
    # 修改一处再比对为False
    f2.write_text(txt + "y", encoding="utf-8")
    assert not fileop.cmp_file(str(f1), str(f2))
    # 时间
    c, m = fileop.get_f_time(str(f1))
    assert c > 0 and m > 0


def test_get_f_last_line(tmp_path):
    f = tmp_path / "x.txt"
    lines = ["a", "b", "last"]
    f.write_text("\n".join(lines), encoding="utf-8")
    last = fileop.get_f_last_line(str(f))
    assert last.strip() == "last"


def test_yaml_load_and_exception(tmp_path):
    f = tmp_path / "good.yml"
    data = {"a": 1}
    import yaml

    f.write_text(yaml.dump(data), encoding="utf-8")
    loaded = fileop.load_yaml(str(f))
    assert loaded["a"] == 1
    # 非法yaml
    bad = tmp_path / "bad.yml"
    bad.write_text("!!!", encoding="utf-8")
    with pytest.raises(FileError):
        fileop.load_yaml(str(bad))
