import dataclasses
from contextlib import asynccontextmanager
from typing import TypeVar, Generic, Optional, ClassVar

from fastapi import FastAPI, Request, Header
from pydantic import BaseModel, PrivateAttr

from smartutils.app.const import HeaderKey
from smartutils.design import deprecated
from smartutils.error.base import BaseError, BaseData

__all__ = ["create_app", "ResponseModel"]

T = TypeVar("T")


class ResponseModel(BaseModel, BaseData, Generic[T]):
    code: int = 0
    msg: str = "success"
    status_code: int = 200
    detail: str = ""
    data: Optional[T] = None

    @classmethod
    def from_error(cls, error: BaseError) -> "ResponseModel":
        return ResponseModel(**error.dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    await init(app.state.smartutils_conf_path)  # noqa

    from smartutils.config import get_config
    from smartutils.log import logger
    from smartutils.error.base import BaseError

    conf = get_config()

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.project.debug
    BaseError.set_debug(conf.project.debug)
    logger.info("!!!======run in {env}======!!!", env="prod" if conf.project.debug else "dev")
    if not conf.project.debug:
        app.docs_url = None

    from smartutils.app.hook import AppHook

    await AppHook.call_startup(app)

    yield

    logger.info("shutdown start close")
    from smartutils.infra import release

    await release()

    await AppHook.call_shutdown(app)

    logger.info("shutdown all closed")


def create_app(conf_path: str = "config/config.yaml"):
    from smartutils.app.factory import ExcJsonResp
    from smartutils.app.main.init_middleware import init_middlewares
    from smartutils.app.const import AppKey
    from smartutils.app.adapter.json_resp.fastapi import STJsonResponse
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException

    key = AppKey.FASTAPI

    app = FastAPI(lifespan=lifespan, default_response_class=STJsonResponse)
    app.state.smartutils_conf_path = conf_path  # noqa

    init_middlewares(app, key)

    @app.exception_handler(RequestValidationError)
    async def _(request: Request, exc: RequestValidationError):
        return ExcJsonResp(key).handle(exc).response

    @app.exception_handler(HTTPException)
    async def _(request: Request, exc: HTTPException):
        return ExcJsonResp(key).handle(exc).response

    @app.get("/")
    def root() -> ResponseModel:
        return ResponseModel()

    @app.get("/healthy")
    def healthy() -> ResponseModel:
        return ResponseModel()

    return app


@deprecated("")
@dataclasses.dataclass
class UserInfo:
    userid: int
    username: str


@deprecated("Info.get_userid Info.get_username")
def get_user_info(
        x_user_id: int = Header(..., alias=HeaderKey.X_USER_ID),
        x_username: str = Header(..., alias=HeaderKey.X_USER_NAME),
) -> UserInfo:
    """
    Deprecated: Use Info.get_userid Info.get_username instead.
    """
    return UserInfo(userid=x_user_id, username=x_username)


@deprecated("Info.get_traceid")
def get_trace_id(x_trace_id: str = Header(..., alias=HeaderKey.X_TRACE_ID)) -> str:
    """
    Deprecated: Use Info.get_traceid instead.
    """
    return x_trace_id
