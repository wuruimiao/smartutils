import pytest
import tempfile
import os
from smartutils.config.init import Config, init, reset, get_config
from smartutils.error.sys import ConfigError, LibraryUsageError
from smartutils.config.schema.project import ProjectConf

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
    # get方法
    assert isinstance(conf.get("project"), ProjectConf)
    assert conf.get("project").name == "test"

def test_config_init_file_not_exist(tmp_path):
    conf = Config(str(tmp_path / "not_exist.yaml"))
    # _config 应包含默认 project 或上次写入的 project
    assert "project" in conf._config
    assert conf._config["project"]["name"] == "test"

def test_config_init_empty(tmp_path):
    yaml_path = tmp_path / "empty.yaml"
    yaml_path.write_text("")
    conf = Config(str(yaml_path))
    assert "project" in conf._config
    assert conf._config["project"]["name"] == "test"

def test_config_project_property(tmp_path):
    yaml_path = tmp_path / "test_config.yaml"
    yaml_path.write_text(project_yaml())
    conf = Config(str(yaml_path))
    assert isinstance(conf.project, ProjectConf)
    assert conf.project.name == "test"

def test_init_and_reset(tmp_path):
    yaml_path = tmp_path / "test_config.yaml"
    yaml_path.write_text(project_yaml())
    c = init(str(yaml_path))
    assert get_config() is c
    reset()
    with pytest.raises(LibraryUsageError):
        get_config()