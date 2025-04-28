import sys
import os

from loguru import logger


class InterceptHandler:
    def write(self, message):
        if message.strip():
            logger.info(message.strip())

    def flush(self):
        pass


def init(log_f_name: str):
    from smartutils.config import config

    logging_conf = config.logging

    os.makedirs(os.path.dirname(logging_conf['file_path']), exist_ok=True)

    file_path = logging_conf['file_path'] % log_f_name

    logger.remove()

    log_format = logging_conf.get(
        'format',
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    logger.add(
        file_path,
        rotation=f"{logging_conf.get('interval', 1)} {logging_conf.get('when', '00:00')}",
        retention=logging_conf.get('backup_count', 7),
        encoding="utf-8",
        enqueue=True,
        level=logging_conf.get('level', 'INFO').upper(),
        format=log_format,
        backtrace=True,
        diagnose=True
    )

    if logging_conf.get('stream', True):
        logger.add(
            sys.stdout,
            level=logging_conf.get('level', 'INFO').upper(),
            format=log_format,
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

    sys.stdout = InterceptHandler()
    sys.stderr = InterceptHandler()
