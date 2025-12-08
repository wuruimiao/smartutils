from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import RunEnv
from smartutils.design import MyBase, SingletonMeta
from smartutils.error.factory import ExcDetailFactory, ExcErrorFactory
from smartutils.log import logger

__all__ = ["ExcJsonRespHandler"]


class ExcJsonRespHandler(MyBase, metaclass=SingletonMeta):
    """
    将异常转换为 JSON 响应的处理器，在中间件中使用。
    """

    def __init__(self):
        self._key = RunEnv.get_app()
        self._resp_fn = JsonRespFactory.get(self._key)

    def handle(self, exc: BaseException) -> ResponseAdapter:
        error = ExcErrorFactory.dispatch(exc)
        logger.exception("{} handle {}", self.name, ExcDetailFactory.dispatch(exc))
        return self._resp_fn(error.as_dict)
