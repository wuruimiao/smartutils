class HeaderKey(str):
    pass


class HEADERKeys:
    X_USER_ID = HeaderKey('X-User-Id')
    X_USER_NAME = HeaderKey('X-User-Name')
    X_TRACE_ID = HeaderKey('X-Trace-ID')
