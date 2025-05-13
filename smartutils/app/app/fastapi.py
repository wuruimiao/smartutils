import dataclasses
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Header

from smartutils.app.const import HeaderKey
from smartutils.design import deprecated

__all__ = ["create_app"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    await init(app.state.smartutils_conf_path)  # noqa

    from smartutils.config import get_config
    from smartutils.log import logger

    import logging

    # 禁止fastapi自带的请求打印
    logging.getLogger("uvicorn.access").disabled = True

    conf = get_config()

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.project.debug
    logger.info(
        "!!!======run in {env}======!!!", env="prod" if conf.project.debug else "dev"
    )
    if not conf.project.debug:
        app.docs_url = None

    from smartutils.app.factory import AppHook

    await AppHook.call_startup(app)

    yield

    logger.info("shutdown start close")
    from smartutils.infra import release

    await release()

    await AppHook.call_shutdown(app)

    logger.info("shutdown all closed")


def create_app(conf_path: str = "config/config.yaml"):
    from smartutils.ret import ResponseModel
    from smartutils.app.adapter.middleware.starletee import StarletteMiddleware
    from smartutils.app.plugin.header import HeaderPlugin
    from smartutils.app.plugin.log import LogPlugin
    from smartutils.app.factory import ExcJsonResp
    from smartutils.app.const import AppKey

    app = FastAPI(lifespan=lifespan)
    app.state.smartutils_conf_path = conf_path  # noqa

    app.add_middleware(StarletteMiddleware, plugin=LogPlugin())
    app.add_middleware(StarletteMiddleware, plugin=HeaderPlugin())

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        return ExcJsonResp.handle(exc, AppKey.FASTAPI)

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
