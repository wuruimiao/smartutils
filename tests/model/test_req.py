from types import SimpleNamespace

import pytest

import smartutils.model.field as req_mod


class DummyModelV1:
    # pydantic1: 有 dict()
    def __init__(self, data):
        self._data = data

    def dict(self, exclude_unset=True):
        return self._data


class DummyModelV2:
    # pydantic2: 有 model_dump()
    def __init__(self, data):
        self._data = data

    def model_dump(self, exclude_unset=True):
        return self._data


def test_explicit_nonnull_fields_pydantic1():
    # 包含None和正常值
    model = DummyModelV1({"a": 1, "b": None, "c": "x"})
    d = req_mod.explicit_nonnull_fields(model)
    assert d == {"a": 1, "c": "x"}


def test_explicit_nonnull_fields_pydantic2():
    # Pydantic2 分支
    model = DummyModelV2({"foo": "bar", "val": 0, "nullval": None})
    d = req_mod.explicit_nonnull_fields(model)
    assert d == {"foo": "bar", "val": 0}


def test_explicit_nonnull_fields_all_none():
    # 全部为None
    model = DummyModelV1({"a": None, "b": None})
    d = req_mod.explicit_nonnull_fields(model)
    assert d == {}


def test_explicit_nonnull_fields_empty():
    # 空
    model = DummyModelV1({})
    d = req_mod.explicit_nonnull_fields(model)
    assert d == {}
