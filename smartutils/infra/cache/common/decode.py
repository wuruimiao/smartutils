class DecodeBytes:
    def __init__(self, redis_decode_responses: bool):
        self._redis_decode_responses = redis_decode_responses
        self._kwargs_key = "my_decode_responses"

    @property
    def redis_decode_responses(self) -> bool:
        return self._redis_decode_responses

    def _do(self, obj):
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        elif isinstance(obj, dict):
            return {self._do(k): self._do(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple, set)):
            typ = type(obj)
            return typ(self._do(item) for item in obj)
        return obj

    def pre(self, args=None, kwargs=None):
        if not kwargs:
            return args, kwargs

        # 从参数中，去掉自定义flag，避免redis方法调用报错
        kwargs = {k: v for k, v in kwargs.items() if k != self._kwargs_key}
        return args, kwargs

    def post(self, result, args=None, kwargs=None):
        # redis解码开启时，不做处理；默认启用解码，除非明确禁用
        if self._redis_decode_responses or (
            not not kwargs and not kwargs.get(self._kwargs_key, True)
        ):
            return result

        return self._do(result)
