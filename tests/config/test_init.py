import pytest

from smartutils.config.init import Config
from smartutils.config.schema.project import ProjectConf
from smartutils.error.sys import ConfigError, LibraryUsageError


def project_yaml():
    return (
        "project:\n"
        "  name: test\n"
        "  id: 1\n"
        "  description: desc\n"
        "  version: v1\n"
        "  key: k\n"
    )


def test_config_init_and_get(tmp_path):
    yaml_path = tmp_path / "test_config.yaml"
    yaml_path.write_text(project_yaml())
    conf = Config(str(yaml_path))
    assert conf._config["project"]["name"] == "test"
    assert isinstance(conf.get("project"), ProjectConf)
    assert conf.get("project").name == "test"  # type: ignore


def test_config_init_file_not_exist(tmp_path):
    conf = Config(str(tmp_path / "not_exist.yaml"))
    assert "project" not in conf._config


def test_config_init_empty(tmp_path):
    yaml_path = tmp_path / "empty.yaml"
    yaml_path.write_text("")
    with pytest.raises(ConfigError):
        Config(str(yaml_path))


def test_config_project_property(tmp_path):
    yaml_path = tmp_path / "test_config.yaml"
    yaml_path.write_text(project_yaml())
    conf = Config(str(yaml_path))
    assert isinstance(conf.project, ProjectConf)
    assert conf.project.name == "test"


def test_init_and_reset(tmp_path):
    yaml_path = tmp_path / "test_config.yaml"
    yaml_path.write_text(project_yaml())
    c = Config.init(str(yaml_path))
    assert Config.get_config() is c
    Config.reset()
    with pytest.raises(LibraryUsageError):
        Config.get_config()


@pytest.fixture
def project_not_required():
    """
    将 project 配置项在 ConfFactory 注册为 require=False，测试后自动还原。
    """
    from smartutils.config.const import ConfKey
    from smartutils.config.factory import ConfFactory
    from smartutils.config.schema.project import ProjectConf

    orig = ConfFactory._registry.copy()
    ConfFactory.register(ConfKey.PROJECT, multi=False, require=False)(ProjectConf)
    yield
    ConfFactory._registry.clear()
    ConfFactory._registry.update(orig)


def test_config_init_missing_key(tmp_path, project_not_required):
    yaml_path = tmp_path / "no_proj.yaml"
    yaml_path.write_text("notproj:\n  a: 1\n")
    conf = Config(str(yaml_path))
    assert conf.get("project") is None


def test_config_project_property_error(tmp_path, project_not_required):
    yaml_path = tmp_path / "error_proj.yaml"
    yaml_path.write_text("notproj:\n  a: 1\n")
    conf = Config(str(yaml_path))
    with pytest.raises(LibraryUsageError):
        _ = conf.project
