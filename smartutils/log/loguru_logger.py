import sys
from pathlib import Path

from loguru import logger


class PrintToLogger:
    def write(self, message):
        message = message.strip()
        if message:
            logger.debug(message)

    def flush(self):
        pass


def init(log_f_name: str = 'app'):
    from smartutils.config import get_config
    logger.remove()

    conf = get_config().loguru
    if not conf:
        logger.info(f'init logger: config no loguru key, do nothing')
        return

    if conf.stream:
        logger.add(
            sys.stdout,
            level=conf.level,
            format=conf.format,
            colorize=True,
            enqueue=conf.enqueue,
        )

    if conf.logdir:
        file_path = Path(conf.logdir) / f'{log_f_name}.log'
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            file_path,
            level=conf.level,
            format=conf.format,
            rotation=conf.rotation,
            retention=conf.retention,
            compression=conf.compression,
            enqueue=conf.enqueue,
            colorize=False,
        )

    if not conf.stream and conf.logdir:
        sys.stdout = PrintToLogger()
        sys.stderr = PrintToLogger()
