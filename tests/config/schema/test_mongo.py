import pytest
from pydantic import ValidationError

from smartutils.config.schema.mongo import MongoConf, MongoHostConf


def make_host(host="localhost", port=27017):
    return MongoHostConf(host=host, port=port)


def make_conf(**kwargs):
    base = dict(
        hosts=[make_host("mongo1", 27017), make_host("mongo2", 27019)],
        user="testuser",
        passwd="testpass",
        db="testdb",
        pool_size=5,
        pool_timeout=10,
        pool_recycle=60,
    )
    base.update(kwargs)
    return MongoConf(**base)


def test_mongohostconf_default_port():
    host = MongoHostConf(host="abc.com")
    assert host.port == 27017
    host2 = MongoHostConf(host="abc.com", port=28000)
    assert host2.port == 28000


def test_mongoconf_required_fields():
    # 缺失user
    with pytest.raises(ValidationError):
        make_conf(user=None)
    # 缺失passwd
    with pytest.raises(ValidationError):
        make_conf(passwd=None)
    # 缺失db
    with pytest.raises(ValidationError):
        make_conf(db=None)
    # hosts不能为空
    with pytest.raises(ValidationError):
        make_conf(hosts=[])


def test_mongoconf_url():
    conf = make_conf(user="u", passwd="p", db="d")
    url = conf.url
    assert url.startswith("mongodb://u:p@mongo1:27017,mongo2:27019/d?")
    assert "replicaSet=myreplset" in url and "authSource=admin" in url


def test_mongoconf_kw_timeouts_and_pool():
    conf = make_conf(
        connect_timeout=11, execute_timeout=5, pool_timeout=7, pool_recycle=13
    )
    kw = conf.kw
    assert kw["connectTimeoutMS"] == 11000
    assert kw["socketTimeoutMS"] == 5000
    assert kw["serverSelectionTimeoutMS"] == 11000
    assert kw["waitQueueTimeoutMS"] == 7000
    assert kw["maxIdleTimeMS"] == 13000
    assert kw["maxLifeTimeMS"] == 13000
    assert kw["maxPoolSize"] == conf.max_pool_size()
    assert kw["minPoolSize"] == conf.min_pool_size()

    # 不传超时参数则为None
    conf2 = make_conf(connect_timeout=None, execute_timeout=None)
    kw2 = conf2.kw
    assert kw2["connectTimeoutMS"] is None
    assert kw2["socketTimeoutMS"] is None
    assert kw2["serverSelectionTimeoutMS"] is None


def test_mongoconf_connect_flag():
    conf = make_conf(connect=True)
    assert conf.connect is True
    conf2 = make_conf(connect=False)
    assert conf2.connect is False
