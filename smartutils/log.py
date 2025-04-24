import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler  # 修改这里

from smartutils.config import config


class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def init(log_f_name: str):
    logging_conf = config.logging
    os.makedirs(os.path.dirname(logging_conf['file_path']), exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging_conf['level'])

    file_path = logging_conf['file_path'] % log_f_name

    file_handler = TimedRotatingFileHandler(
        file_path,
        when=logging_conf.get('when', 'midnight'),
        interval=logging_conf.get('interval', 1),
        backupCount=logging_conf['backup_count'],
        encoding='utf-8'
    )
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(logging_conf['format'])
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    if logging_conf['stream']:
        logger.addHandler(stream_handler)

    # Redirect stdout and stderr to logger
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
