import asyncio
import os


async def test_loguru_logger_with_temp_config(tmp_path):
    config_str = (
        """
loguru:
  stream: false
  logdir: "%s"
  level: "DEBUG"
  rotation: "1 MB"
  retention: "3 days"
  compression: "zip"
  enqueue: true
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""
        % tmp_path
    )
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.init import init

    init(str(config_file))

    from smartutils.infra.log.loguru import logger

    logger.debug("hello test loguru logger")

    log_file = os.path.join(tmp_path, "auth.log")
    assert os.path.exists(log_file)
    # 等待写入
    await asyncio.sleep(0.3)
    with open(log_file, "r") as f:
        content = f.read()
    assert "hello test loguru logger" in content

    from smartutils.design._singleton import reset_all

    reset_all()


async def test_loguru_logger_print_to_logger(tmp_path):
    """
    stream: false 时，print 被 PrintToLogger 捕获，写入日志
    """
    config_str = (
        """
loguru:
  stream: false
  logdir: "%s"
  level: "DEBUG"
  rotation: "1 MB"
  retention: "3 days"
  compression: "zip"
  enqueue: true
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""
        % tmp_path
    )
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.init import init

    init(str(config_file))

    # PrintToLogger生效，print被记录
    print("this is printed and should be in the log file")

    from smartutils.infra.log.loguru import logger

    logger.debug("logger debug also in log file")

    log_file = os.path.join(tmp_path, "auth.log")
    assert os.path.exists(log_file)
    # 等待写入
    await asyncio.sleep(0.3)
    with open(log_file, "r") as f:
        content = f.read()
    assert "this is printed and should be in the log file" in content
    assert "logger debug also in log file" in content

    from smartutils.design._singleton import reset_all

    reset_all()


async def test_loguru_logger_stream_true(tmp_path, capsys):
    """
    stream: true 时，print 只会输出到控制台，不进日志文件
    """
    config_str = (
        """
loguru:
  stream: true
  logdir: "%s"
  level: "DEBUG"
  format: "<level>{message}</level>"
  rotation: "1 MB"
  retention: "3 days"
  compression: "zip"
  enqueue: true
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""
        % tmp_path
    )
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils.init import init

    init(str(config_file))

    # 打印一条消息
    print("this should NOT be in the log file, only in stdout")

    from smartutils.log import logger

    logger.debug("logger debug in log file")

    log_file = os.path.join(tmp_path, "auth.log")
    await asyncio.sleep(0.3)
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        content = f.read()
    # print内容不在日志文件
    assert "this should NOT be in the log file" not in content
    # logger内容在日志文件
    assert "logger debug in log file" in content

    # 检查stdout有print内容
    captured = capsys.readouterr()
    assert "this should NOT be in the log file, only in stdout" in captured.out

    from smartutils.design._singleton import reset_all

    reset_all()


async def test_loguru_logger_no_config():
    """
    stream: true 时，print 只会输出到控制台，不进日志文件
    """
    from smartutils.init import init

    init()

    from smartutils.log import logger

    logger.debug("logger debug in log file")

    from smartutils.design._singleton import reset_all

    reset_all()
