import io
import os
import shutil
import zipfile

import pytest

from smartutils.file import _compress as compress_mod

TMP_DIR = "./tmp_compress_test"


def setup_module(module):
    os.makedirs(TMP_DIR, exist_ok=True)
    # 创建一个文本文件
    with open(f"{TMP_DIR}/a.txt", "w") as f:
        f.write("hello zip")


def teardown_module(module):
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    zip_path = f"{TMP_DIR}.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)


def test_is_compress_file():
    # 支持、非支持后缀
    assert compress_mod.is_compress_file("file.txt") is False
    assert compress_mod.is_compress_file("file.zip") is True
    assert (
        compress_mod.is_compress_file("file.tar.gz") is True
    )  # 仅对最后一段后缀判断，此设计
    assert compress_mod.is_compress_file("file.gz") is True
    assert compress_mod.is_compress_file("file") is False


def test_compress_and_extract():
    # 测试压缩
    zip_path, err = compress_mod.compress(TMP_DIR)
    assert zip_path.endswith(".zip")
    assert err.is_ok
    assert os.path.exists(zip_path)

    # 解压到新目录
    extract_dir = TMP_DIR + "/extracted"
    os.makedirs(extract_dir, exist_ok=True)
    extract_err = compress_mod.extract_compressed(zip_path, extract_dir)
    assert extract_err.is_ok
    assert os.path.exists(os.path.join(extract_dir, "a.txt"))


def test_check_zip_file():
    zip_path, _ = compress_mod.compress(TMP_DIR)
    # 完好zip
    err = compress_mod.check_zip_file(zip_path)
    assert err.is_ok
    # 不存在文件
    err2 = compress_mod.check_zip_file("not_exist.zip")
    assert not err2.is_ok
    # 非zip类型
    bad_path = os.path.join(TMP_DIR, "bad.txt")
    with open(bad_path, "wb") as f:
        f.write(b"not a zip")
    err3 = compress_mod.check_zip_file(bad_path)
    assert not err3.is_ok


def test_decode_gzip():
    import gzip

    raw = b"hello world test"
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb") as gz:
        gz.write(raw)
    b_gzip = out.getvalue()
    # 解码成功
    assert compress_mod.decode_gzip(b_gzip) == raw
    # 解码失败时直接返回原始
    assert compress_mod.decode_gzip(b"not gzip data") == b"not gzip data"
