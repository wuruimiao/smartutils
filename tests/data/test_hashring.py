import pytest
from unittest.mock import MagicMock
import types
import smartutils.data.hashring as hashring_mod


@pytest.fixture
def mock_hashring(monkeypatch):
    class DummyHashRing:
        def __init__(self, nodes=None, **kwargs):
            self.runtime = types.SimpleNamespace(
                _nodes={"a": {"weight": 1}, "b": {"weight": 2}},
                _ring={1: "a", 2: "b", 3: "b"},
            )

        def __init_subclass__(cls):
            pass

    monkeypatch.setattr(hashring_mod, "_HashRing", DummyHashRing)
    return DummyHashRing


def test_hashring_init(mock_hashring):
    ring = hashring_mod.HashRing(["a", "b"])
    assert hasattr(ring, "_real_node")
    assert hasattr(ring, "_sorted_node")


def test_hashring_empty_nodes(mock_hashring):
    ring = hashring_mod.HashRing()
    assert hasattr(ring, "_real_node")
    assert hasattr(ring, "_sorted_node")


def test_hashring_node_weight():
    # 假设HashRing支持接收 dict 作为节点和权重
    ring = hashring_mod.HashRing({"a": 1, "b": 2})
    # 通过runtime._nodes访问节点权重
    assert ring.runtime._nodes["a"]["weight"] == 1
    assert ring.runtime._nodes["b"]["weight"] == 2


def test_hashring_get_next_nodes(mock_hashring):
    ring = hashring_mod.HashRing(["a", "b"])
    next_nodes = ring.get_node_next_nodes("a")
    assert "b" in next_nodes
    # 对于最后一个节点，应返回第一个节点
    next_nodes = ring.get_node_next_nodes("b")
    assert "a" in next_nodes


def test_hashring_edge_cases(mock_hashring):
    ring = hashring_mod.HashRing(["a"])
    # 单节点的情况
    assert ring.get_node_next_nodes("a") == ["a"]
    # 不存在的节点
    assert ring.get_node_next_nodes("not_exist") == []
