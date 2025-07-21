import os
from contextlib import asynccontextmanager
from typing import Generic, Optional, TypeVar

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

from smartutils.app.const import CONF_ENV_NAME
from smartutils.error.base import BaseData, BaseError
from smartutils.error.sys import LibraryError

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
        return ResponseModel(**error.as_dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    init(app.state.smartutils_conf_path)

    from smartutils.config import Config
    from smartutils.error.base import BaseError
    from smartutils.log import logger

    conf = Config.get_config()

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.project.debug
    BaseError.set_debug(conf.project.debug)
    logger.info(
        "!!!======run in {env}======!!!", env="prod" if conf.project.debug else "dev"
    )
    if not conf.project.debug:
        app.docs_url = None

    from smartutils.app.hook import AppHook

    await AppHook.call_startup(app)

    yield

    logger.info("shutdown start close")
    from smartutils.init import release

    await release()

    await AppHook.call_shutdown(app)

    logger.info("shutdown all closed")


def create_app():
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException

    from smartutils.app.adapter.json_resp._fastapi import STJsonResponse
    from smartutils.app.adapter.middleware.manager import MiddlewareManager
    from smartutils.app.const import AppKey
    from smartutils.app.factory import ExcJsonResp
    from smartutils.init import init

    key = AppKey.FASTAPI

    app = FastAPI(lifespan=lifespan, default_response_class=STJsonResponse)

    conf_path = os.getenv(CONF_ENV_NAME, None)
    if not conf_path:
        raise LibraryError(f"env {CONF_ENV_NAME} is not set")
    app.state.smartutils_conf_path = conf_path

    # TODO: 初始化一次，这里是为了middleware初始化能读取配置
    init(conf_path)
    MiddlewareManager().init_app_middlewares(app, key)

    @app.exception_handler(RequestValidationError)
    async def _(request: Request, exc: RequestValidationError):
        return ExcJsonResp(key).handle(exc).response

    @app.exception_handler(HTTPException)
    async def _(request: Request, exc: HTTPException):
        return ExcJsonResp(key).handle(exc).response

    router = APIRouter(route_class=MiddlewareManager().init_default_route_middleware())

    @router.get("/")
    def root() -> ResponseModel:
        return ResponseModel()

    @router.get("/healthy")
    def healthy() -> ResponseModel:
        return ResponseModel()

    app.include_router(router)

    return app
