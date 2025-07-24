import pytest
from pydantic import ValidationError

from smartutils.config.schema.host import HostConf
from smartutils.config.schema.kafka import KafkaConf


def valid_kafka_conf(**kwargs):
    return {
        "bootstrap_servers": [HostConf(host="127.0.0.1", port=9092)],
        "client_id": "test-client",
        "acks": "all",
        "compression_type": None,
        "max_batch_size": 16384,
        "linger_ms": 100,
        "request_timeout_ms": 5000,
        "retry_backoff_ms": 300,
        **kwargs,
    }


def test_kafka_conf_valid():
    conf = KafkaConf(**valid_kafka_conf())
    assert conf.urls == ["127.0.0.1:9092"]
    assert conf.client_id == "test-client"
    assert conf.acks == "all"
    assert conf.compression_type is None
    assert conf.max_batch_size == 16384
    assert conf.linger_ms == 100
    assert conf.request_timeout_ms == 5000
    assert conf.retry_backoff_ms == 300


@pytest.mark.parametrize("acks", ["all", 1, 0])
def test_kafka_conf_acks_valid(acks):
    conf = KafkaConf(**valid_kafka_conf(acks=acks))
    assert conf.acks == acks


@pytest.mark.parametrize("acks", ["2", 2, "none"])
def test_kafka_conf_acks_invalid(acks):
    conf_dict = valid_kafka_conf(acks=acks)
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert (
        "1 validation error for KafkaConf\nacks\n  Input should be 'all', 1 or 0"
        in str(exc.value)
    )


@pytest.mark.parametrize("compression_type", ["zstd", "snappy", None])
def test_kafka_conf_compression_type_valid(compression_type):
    conf = KafkaConf(**valid_kafka_conf(compression_type=compression_type))
    assert conf.compression_type == compression_type


@pytest.mark.parametrize("compression_type", ["gzip", "zip", 123])
def test_kafka_conf_compression_type_invalid(compression_type):
    conf_dict = valid_kafka_conf(compression_type=compression_type)
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert (
        "1 validation error for KafkaConf\ncompression_type\n  Input should be 'zstd', 'snappy' or None"
        in str(exc.value)
    )


def test_kafka_conf_bootstrap_servers_empty():
    conf_dict = valid_kafka_conf(bootstrap_servers=[])
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "bootstrap_servers" in str(exc.value)
    assert "at least 1 item" in str(exc.value)


def test_kafka_conf_bootstrap_servers_invalid_type():
    conf_dict = valid_kafka_conf(bootstrap_servers=["not_a_hostconf"])
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "bootstrap_servers" in str(exc.value)
    assert "HostConf" in str(exc.value)


def test_kafka_conf_empty_client_id():
    conf_dict = valid_kafka_conf(client_id="")
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "String should have at least 1 character" in str(exc.value)
    assert "client_id" in str(exc.value)


@pytest.mark.parametrize(
    "field", ["request_timeout_ms", "retry_backoff_ms", "max_batch_size"]
)
@pytest.mark.parametrize("value", [-1, 0])
def test_kafka_conf_le_0(field, value):
    conf_dict = valid_kafka_conf()
    conf_dict[field] = value
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "Input should be greater than 0" in str(exc.value)
    assert field in str(exc.value)


@pytest.mark.parametrize("value", [-1, -2])
def test_kafka_conf_lt_0(value):
    conf_dict = valid_kafka_conf(linger_ms=value)
    with pytest.raises(ValidationError) as exc:
        KafkaConf(**conf_dict)
    assert "Input should be greater than or equal to 0" in str(exc.value)
    assert "linger_ms" in str(exc.value)


def test_kafka_conf_kw():
    kw = KafkaConf(**valid_kafka_conf()).kw
    assert "host" not in kw
    assert "port" not in kw
    assert "bootstrap_servers" not in kw
    assert kw["client_id"] == "test-client"
    assert kw["acks"] == "all"
