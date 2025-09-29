def test_main_init_exception(mocker, capsys):
    # exit_on_fail 打补丁，防止直接退出
    mock_exit = mocker.patch("smartutils.call.exit_on_fail")
    from smartutils.config import Config

    mocker.patch.object(Config, "init", side_effect=Exception("Test Exception"))
    from smartutils.init import init

    init()

    # 断言 exit_on_fail 被调用，说明异常被正确捕获
    mock_exit.assert_called_once()

    # 捕获 print 输出，断言包含特定异常信息
    captured = capsys.readouterr()
    assert "Smartutils init fail for" in captured.out
    assert "App Exit." in captured.out


def test_main_init_custom_project_config(tmp_path_factory):
    config_str = """
project:
  test_a: 2
"""
    config_file = tmp_path_factory.mktemp("config") / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    from smartutils.config._config import Config
    from smartutils.config.schema.project import ProjectConf

    class MyConf(ProjectConf):
        test_a: int = 1

    from smartutils.init import init

    init(conf_path=str(config_file), project_conf_cls=MyConf)

    assert Config.get_config().project.test_a == 2
