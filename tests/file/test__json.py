import os
import tempfile
import json
import yaml
import shutil
import pytest

from smartutils.file import _json
from smartutils.error.sys import NoFileError, FileInvalidError

def test_load_json_f_not_exist(tmp_path):
    # 文件不存在应返回空dict+NoFileError
    res, err = _json.load_json_f(str(tmp_path/'not_exist.json'))
    assert res == {}
    assert isinstance(err, NoFileError)

def test_load_json_f_invalid_json(tmp_path):
    # 非法json内容应捕获并返回FileInvalidError
    file_path = tmp_path/'invalid.json'
    file_path.write_text('not_a_json', encoding='utf-8')
    res, err = _json.load_json_f(str(file_path))
    assert res == {}
    assert isinstance(err, FileInvalidError)

def test_load_json_f_valid_json(tmp_path):
    data = {'a': 1, 'b': '2'}
    file_path = tmp_path/'valid.json'
    file_path.write_text(json.dumps(data), encoding='utf-8')
    res, err = _json.load_json_f(str(file_path))
    assert res == data
    assert err.is_ok

def test_dump_json_f_and_read(tmp_path):
    data = {'foo': 'bar', 'list': [1, 2, 3]}
    file_path = tmp_path/'dump.json'
    err = _json.dump_json_f(str(file_path), data)
    assert err.is_ok
    # 检查写入后可正确读出
    with open(file_path, encoding='utf-8') as f:
        loaded = json.load(f)
    assert loaded == data

def test_compare_json_f_equal(tmp_path):
    data = {"x": 42, "y": [1,2]}
    f1 = tmp_path/'f1.json'
    f2 = tmp_path/'f2.json'
    f1.write_text(json.dumps(data), encoding='utf-8')
    f2.write_text(json.dumps(data), encoding='utf-8')
    assert _json.compare_json_f(str(f1), str(f2))

def test_compare_json_f_not_equal(tmp_path):
    f1 = tmp_path/'a.json'
    f2 = tmp_path/'b.json'
    f1.write_text(json.dumps({"v": 1}), encoding='utf-8')
    f2.write_text(json.dumps({"v": 2}), encoding='utf-8')
    assert not _json.compare_json_f(str(f1), str(f2))

def test_compare_json_f_file_not_exist(tmp_path):
    # 两文件其中之一不存在应返回False
    f1 = tmp_path/'file_exist.json'
    f1.write_text(json.dumps({"v": 1}), encoding='utf-8')
    assert not _json.compare_json_f(str(f1), str(tmp_path/'no_such_file.json'))

def test_compare_json_f_with_exclude(tmp_path):
    # 指定exclude_field应跳过该字段
    f1 = tmp_path/'f1.json'
    f2 = tmp_path/'f2.json'
    d1 = {"a": 1, "b": 2}
    d2 = {"a": 999, "b": 2}
    f1.write_text(json.dumps(d1), encoding='utf-8')
    f2.write_text(json.dumps(d2), encoding='utf-8')
    # 排除"a"后应视为相等
    assert _json.compare_json_f(str(f1), str(f2), exclude_field={"a"})

def test_tran_json_to_yml_f_success(tmp_path):
    # 可以正确生成yaml内容
    d = {"hello": [1,2,3], "val": "abc"}
    src = tmp_path/'src.json'
    dst = tmp_path/'dst.yml'
    src.write_text(json.dumps(d), encoding='utf-8')
    _json.tran_json_to_yml_f(str(src), str(dst))
    assert dst.exists()
    loaded = yaml.safe_load(dst.read_text(encoding='utf-8'))
    assert loaded == d

def test_tran_json_to_yml_f_json_not_exist(tmp_path):
    # 源json不存在，不会生成yml
    src = tmp_path/'no.json'
    dst = tmp_path/'to.yml'
    _json.tran_json_to_yml_f(str(src), str(dst))
    assert not dst.exists()

def test_tran_json_to_yml_f_dst_already_exists(tmp_path):
    # 目标yml已存在，不应覆盖
    d = {"foo": 1}
    src = tmp_path/'a.json'
    dst = tmp_path/'b.yml'
    src.write_text(json.dumps(d), encoding='utf-8')
    dst.write_text("origin: true", encoding='utf-8')
    _json.tran_json_to_yml_f(str(src), str(dst))
    # 原内容未变
    assert dst.read_text(encoding='utf-8') == "origin: true"
