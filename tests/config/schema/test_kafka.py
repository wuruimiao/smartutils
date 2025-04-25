import pytest
from pydantic import ValidationError
from smartutils.config.schema.host import HostConf
from smartutils.config.schema.kafka import KafkaConf


def valid_kafka_conf(**kwargs):
    # 构造合法的配置字典
    return {
        "bootstrap_servers": [HostConf(host="127.0.0.1", port=9092)],
        "client_id": "test-client",
        "acks": 'all',
        "compression_type": None,
        "max_batch_size": 16384,
        "linger_ms": 100,
        "request_timeout_ms": 5000,
        "retry_backoff_ms": 300,
        **kwargs
    }


def test_kafka_conf_valid():
    conf = KafkaConf(**valid_kafka_conf())
    assert conf.client_id == "test-client"
    assert conf.max_batch_size == 16384


@pytest.mark.parametrize("field,value,errmsg", [
    ("max_batch_size", 0, "max_batch_size must be positive"),
    ("max_batch_size", -10, "max_batch_size must be positive"),
    ("linger_ms", -1, "linger_ms must be non-negative"),
    ("request_timeout_ms", -5, "request_timeout_ms must be non-negative"),
    ("retry_backoff_ms", -2, "retry_backoff_ms must be non-negative"),
    ("client_id", "", "client_id must not be empty"),
    ("client_id", "   ", "client_id must not be empty"),
])
def test_kafka_conf_invalid_fields(field, value, errmsg):
    conf_dict = valid_kafka_conf(**{field: value})
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert errmsg in str(exc.value)


@pytest.mark.parametrize("acks", ['all', 1, 0])
def test_kafka_conf_acks_valid(acks):
    conf = KafkaConf(**valid_kafka_conf(acks=acks))
    assert conf.acks == acks


@pytest.mark.parametrize("acks", ['2', 2, 'none'])
def test_kafka_conf_acks_invalid(acks):
    conf_dict = valid_kafka_conf(acks=acks)
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "Input should be" in str(exc.value) or "unexpected value" in str(exc.value)


@pytest.mark.parametrize("compression_type", ['zstd', 'snappy', None])
def test_kafka_conf_compression_type_valid(compression_type):
    conf = KafkaConf(**valid_kafka_conf(compression_type=compression_type))
    assert conf.compression_type == compression_type


@pytest.mark.parametrize("compression_type", ['gzip', 'zip', 123])
def test_kafka_conf_compression_type_invalid(compression_type):
    conf_dict = valid_kafka_conf(compression_type=compression_type)
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "Input should be" in str(exc.value) or "unexpected value" in str(exc.value)


def test_kafka_conf_bootstrap_servers_empty():
    conf_dict = valid_kafka_conf(bootstrap_servers=[])
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "bootstrap_servers" in str(exc.value) or "at least 1 item" in str(exc.value)


def test_kafka_conf_bootstrap_servers_invalid_type():
    conf_dict = valid_kafka_conf(bootstrap_servers=["not_a_hostconf"])
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "bootstrap_servers" in str(exc.value) or "HostConf" in str(exc.value)
