"""
不要在项目启动后抛出异常
"""


class LibraryUsageError(Exception):
    pass


class FileError(Exception):
    pass
