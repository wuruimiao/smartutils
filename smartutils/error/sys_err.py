from smartutils.error.base import BaseError


class SysError(BaseError):
    pass


class ValidationError(SysError):
    code = 1001
    msg = "Validation Error"
    status_code = 422


class TimeOutError(SysError):
    code = 1002
    msg = "Request Timeout"
    status_code = 408  # 标准 HTTP


class LibraryError(SysError):
    code = 1009
    msg = "Library Error"
    status_code = 500


class LibraryUsageError(SysError):
    code = 1003
    msg = "Library Usage Error"
    status_code = 500


class FileError(SysError):
    code = 1011
    msg = "File Error"
    status_code = 500


class ConfigError(SysError):
    code = 1010
    msg = "Config Error"
    status_code = 500


class ExternalServiceError(SysError):
    code = 1004
    msg = "External Service Error"
    status_code = 502


class UnsupportedError(SysError):
    code = 1005
    msg = "Unsupported Operation"
    status_code = 405


class RequestTooLargeError(SysError):
    code = 1006
    msg = "Request Too Large"
    status_code = 413


class DatabaseError(SysError):
    code = 1007
    msg = "Database Error"
    status_code = 500


class CacheError(SysError):
    code = 1008
    msg = "Cache Error"
    status_code = 500


class MQError(SysError):
    code = 1009
    msg = "Message Queue Error"
    status_code = 500
