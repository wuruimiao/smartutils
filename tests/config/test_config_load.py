import pytest

from smartutils.config.const import ConfKey
from smartutils.config.schema.canal import CanalConf
from smartutils.config.schema.kafka import KafkaConf
from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.config.schema.project import ProjectConf
from smartutils.config.schema.redis import RedisConf
from smartutils.error.sys import LibraryUsageError


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    #     config_str = """

    # """

    #     tmp_dir = tmp_path_factory.mktemp("config")
    #     config_file = tmp_dir / "test_config.yaml"
    #     with open(config_file, "w") as f:
    #         f.write(config_str)
    # yield config_file
    yield "tests/config/config_for_test_config.yaml"


def test_config_load_db_url(setup_config: str):
    from smartutils.config import Config

    assert Config.init(setup_config)

    config = Config.get_config().get_typed(ConfKey.MYSQL, MySQLConf, expect_dict=True)
    assert config is not None
    assert config["default"].url == "mysql+asyncmy://root:naobo@localhost:3306/test_db"

    config = Config.get_config().get_typed(
        ConfKey.POSTGRESQL, PostgreSQLConf, expect_dict=True
    )
    assert config is not None
    assert (
        config["default"].url
        == "postgresql+asyncpg://root:naobo@localhost:5432/test_db"
    )

    config = Config.get_config().get_typed(ConfKey.REDIS, RedisConf, expect_dict=True)
    assert config is not None
    assert config["default"].url == "redis://localhost:6379"

    config = Config.get_config().get_typed(ConfKey.KAFKA, KafkaConf, expect_dict=True)
    assert config is not None
    assert config["default"].urls == ["localhost:19092", "127.0.0.1:9093"]

    config = Config.get_config().get_typed(ConfKey.CANAL, CanalConf, expect_dict=True)
    assert config is not None
    assert config["default"].clients[0].name == "c1"


def test_config_load_tencentcloud(setup_config: str):
    from smartutils.config import Config

    assert Config.init(setup_config)

    config = Config.get_config()

    from smartutils.config.const import ConfKey
    from smartutils.config.schema.tencent_cloud import TencentCloudConf

    tx_map = config.get_typed(ConfKey.TENCENTCLOUD, TencentCloudConf, expect_dict=True)
    assert tx_map is not None
    tx = tx_map["default"]
    assert tx.secret_id == "sida"
    assert tx.secret_key == "skeyb"
    assert tx.role_arn == "rarnc"
    assert tx.on_cvm is True
    assert tx.sts_refresh is False
    assert tx.sts_ttl == 11111
    assert tx.resource[0].policy == {
        "version": "2.0",
        "statement": [
            {
                "action": ["name/cos:PutObject", "name/cos:PostObject"],
                "condition": {
                    "string_equal": {
                        "qcs:request_tag": ["部门&研发部1"],
                        "qcs:resource_tag": ["部门&研发部"],
                    }
                },
                "effect": "allow",
                "resource": [
                    "qcs::cos:shanghai:uid/1303961000:clean-test-1303961000/*"
                ],
            },
            {
                "action": ["name/cos:*"],
                "condition": {
                    "ip_equal": {"qcs:ip": ["10.217.182.3/24", "111.21.33.72/24"]}
                },
                "effect": "deny",
                "resource": [
                    "qcs::cos:shanghai:uid/1303961000:clean-test-1303961000/default/*"
                ],
            },
        ],
    }
    assert tx.resource[1].policy is None
    assert tx.resource[2].policy == {
        "statement": [
            {
                "action": ["name/cos:PutObject", "name/cos:PostObject"],
                "condition": None,
                "effect": "allow",
                "resource": [
                    "qcs::cos:shanghai:uid/1303961002:clean-test-1303961002/*"
                ],
            }
        ],
        "version": "2.0",
    }


def test_config_load_project(setup_config: str):
    from smartutils.config import Config

    assert Config.init(setup_config)

    config = Config.get_config()
    assert config.project.name == "auth"
    assert config.project.description == "test_auth"
    assert config.project.version == "0.0.1"
    assert not hasattr(config.project, "key")


def test_project_conf_inherit(setup_config: str):
    from smartutils.config import ConfFactory, Config, ConfKey, ProjectConf

    @ConfFactory.register(ConfKey.PROJECT)
    class MyProjectConf(ProjectConf):
        key: str

    Config.init(setup_config)
    conf = Config.get_config()
    assert conf.project_typed(MyProjectConf).key == "test_key"


def test_config_get_typed_abnormal(setup_config: str):
    from smartutils.config import Config

    assert Config.init(setup_config)

    config = Config.get_config()
    assert config.get_typed(ConfKey.GROUP_DEFAULT, ProjectConf) is None

    with pytest.raises(LibraryUsageError) as exc:
        config.get_typed(ConfKey.PROJECT, ProjectConf, expect_dict=True)
    assert str(exc.value) == "Value for project is not a dict, but expect_dict=True"
