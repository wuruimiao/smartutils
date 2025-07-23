import os

import pytest

from smartutils.file import _fileop


def test_dump_and_load_text(tmp_path):
    f = tmp_path / "a.txt"
    assert _fileop.dump_f(str(f), "hello\nworld").is_ok
    content, err = _fileop.load_f(str(f))
    assert "hello" in content and err.is_ok
    lines, err = _fileop.load_f_line(str(f))
    assert lines[0] == "hello" and err.is_ok
    assert _fileop.dump_f_lines(str(f), ["a", "b"]).is_ok


def test_dump_and_load_bytes(tmp_path):
    f = tmp_path / "b.bin"
    assert _fileop.dump_b_f(str(f), b"abc\x01").is_ok
    with open(f, "rb") as ff:
        val = ff.read()
    assert val == b"abc\x01"


def test_append_lines(tmp_path):
    f = tmp_path / "c.txt"
    assert _fileop.append_f_line(str(f), "x1").is_ok
    assert _fileop.append_f_line(str(f), "x2", line_break=False).is_ok
    assert _fileop.append_f_lines(str(f), ["l3", "l4"]).is_ok


def test_rm_and_nonexist(tmp_path):
    f = tmp_path / "todel.txt"
    assert _fileop.dump_f(str(f), "abc").is_ok
    assert _fileop.rm_file(str(f)).is_ok
    assert _fileop.rm_file(str(f)).is_ok


def test_copy_move_file(tmp_path):
    f = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    _fileop.dump_f(str(f), "hello")
    d, err = _fileop.copy_file(str(f), str(f2))
    assert err.is_ok
    assert os.path.exists(d)
    f3 = tmp_path / "f3.txt"
    assert _fileop.move_file(str(f2), str(f3)).is_ok
    assert os.path.exists(f3)


def test_sha2_and_cmp(tmp_path):
    f1 = tmp_path / "fsha1.txt"
    f2 = tmp_path / "fsha2.txt"
    _fileop.dump_f(str(f1), "abcdefg")
    _fileop.dump_f(str(f2), "abcdefg")
    h1 = _fileop.sha2_file(str(f1))
    h2 = _fileop.sha2_file(str(f2))
    assert h1 == h2
    assert _fileop.cmp_file(str(f1), str(f2)) is True


def test_get_f_time(tmp_path):
    f = tmp_path / "t.txt"
    _fileop.dump_f(str(f), "tt")
    c, m = _fileop.get_f_time(str(f))
    assert isinstance(c, float) and isinstance(m, float)


def test_get_f_last_line(tmp_path):
    f = tmp_path / "last.txt"
    _fileop.dump_f(str(f), "a\nb\ncc")
    last = _fileop.get_f_last_line(str(f))
    assert last.strip() == "cc"


def test_is_binary(tmp_path):
    f = tmp_path / "bin.dat"
    with open(f, "wb") as ff:
        ff.write(b"\x00\x01\x02")
    assert _fileop.is_binary_f(str(f)) is True


def test_load_f_line_unicode_error(tmp_path):
    f = tmp_path / "err.txt"
    f.write_bytes(b"\xff\xff\x00notutf8")
    ret, err = _fileop.load_f_line(str(f))
    assert not ret and not err.is_ok


def test_merge_file(tmp_path):
    f1 = tmp_path / "merge1.txt"
    f2 = tmp_path / "merge2.txt"
    _fileop.dump_f_lines(str(f1), ["aa"])
    _fileop.dump_f_lines(str(f2), ["bb"])
    _fileop.merge_file(str(f1), str(f2))
    x, _ = _fileop.load_f_line(str(f1))
    assert "bb" in x and "aa" in x


def test_copy_dir_and_override(tmp_path):
    d1 = tmp_path / "src"
    d2 = tmp_path / "dst"
    d1.mkdir()
    file1 = d1 / "a.txt"
    file1.write_text("123")
    count = _fileop.copy_dir(str(d1), str(d2))
    assert count == 1
    count2 = _fileop.copy_dir(str(d1), str(d2))
    assert count2 == 0
    count3 = _fileop.copy_dir(str(d1), str(d2), override=True)
    assert count3 == 1


def test_link_and_rm_link(tmp_path, mocker):
    src = tmp_path / "srcdir"
    dst = tmp_path / "alink"
    src.mkdir()

    def fake_is_win():
        return False

    mocker.patch.object(_fileop, "is_win", fake_is_win)
    ret = _fileop.link(str(src), str(dst))
    assert ret.is_ok and os.path.islink(dst)
    ret2 = _fileop.link(str(src), str(dst))
    assert ret2.is_ok
    ret3 = _fileop.rm_link(str(dst))
    assert ret3.is_ok
    ret4 = _fileop.rm_link(str(src))
    assert not ret4.is_ok


def test_read_file_iter(tmp_path):
    f = tmp_path / "rfile.bin"
    buf = b"abcde" * 100
    f.write_bytes(buf)
    out = b""
    for chunk in _fileop.read_file_iter(str(f)):
        if chunk:
            out += chunk
    assert out == buf


def test_is_binary_f2(tmp_path):
    f = tmp_path / "bin1"
    f.write_bytes(b"\xff\xfe\x00\x00")
    assert _fileop.is_binary_f2(str(f)) is False
    t = tmp_path / "txt1"
    t.write_text("abc")
    assert _fileop.is_binary_f2(str(t)) is True


def test_save_content_and_merge(tmp_path):
    subdir = tmp_path / "dir"
    subdir.mkdir()
    filename = "out.txt"
    with _fileop.save_content(str(subdir), filename) as tmpf:
        with open(tmpf, "w") as f:
            f.write("smart line")
    out_f = subdir / filename
    assert out_f.exists()
    assert (subdir / "__dir.txt").exists()
    with _fileop.save_content(str(subdir), filename, merge=True) as tmpf:
        with open(tmpf, "w") as f:
            f.write("new line")
    assert out_f.exists()


def test_load_yaml(tmp_path):
    yml = tmp_path / "a.yml"
    yml.write_text("a: 123\nb: true")
    out = _fileop.load_yaml(str(yml))
    assert out["a"] == 123 and out["b"] is True
    yml.write_text("a: [unclosed")
    with pytest.raises(Exception):
        _fileop.load_yaml(str(yml))
