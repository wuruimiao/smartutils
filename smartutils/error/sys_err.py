from smartutils.error.base import BaseError


class SysError(BaseError):
    pass


class ValidationError(SysError):
    code = 1001
    msg = "Validation Error"
    status_code = 422  # Unprocessable Entity


class TimeOutError(SysError):
    code = 1002
    msg = "Request Timeout"
    status_code = 408  # Request Timeout


class LibraryUsageError(SysError):
    code = 1003
    msg = "Library Usage Error"
    status_code = 500  # Internal Server Error


class ExternalServiceError(SysError):
    code = 1004
    msg = "External Service Error"
    status_code = 500  # Internal Server Error


class UnsupportedError(SysError):
    code = 1005
    msg = "Unsupported Operation"
    status_code = 405  # Method Not Allowed


class UnsupportedMediaTypeError(SysError):
    code = 1006
    msg = "Unsupported Media Type"
    status_code = 415  # Unsupported Media Type


class RequestTooLargeError(SysError):
    code = 1007
    msg = "Request Too Large"
    status_code = 413  # Payload Too Large


class DatabaseError(SysError):
    code = 1008
    msg = "Database Error"
    status_code = 500  # Internal Server Error


class CacheError(SysError):
    code = 1009
    msg = "Cache Error"
    status_code = 500  # Internal Server Error


class LibraryError(SysError):
    code = 1009
    msg = "Library Error"
    status_code = 500  # Internal Server Error


class ConfigError(SysError):
    code = 1010
    msg = "Config Error"
    status_code = 500  # Internal Server Error


class FileError(SysError):
    code = 1011
    msg = "File Error"
    status_code = 500  # Internal Server Error


class MQError(SysError):
    code = 1012
    msg = "Message Queue Error"
    status_code = 500  # Internal Server Error
