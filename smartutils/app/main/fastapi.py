import dataclasses
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Header
from fastapi.exceptions import RequestValidationError

from smartutils.app.const import HeaderKey
from smartutils.design import deprecated

__all__ = ["create_app"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    await init(app.state.smartutils_conf_path)  # noqa

    from smartutils.config import get_config
    from smartutils.log import logger

    conf = get_config()

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.project.debug
    logger.info("!!!======run in {env}======!!!", env="prod" if conf.project.debug else "dev")
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
    from smartutils.app.adapter.middleware.factory import MiddlewareFactory
    from smartutils.app.adapter.req.factory import RequestAdapterFactory
    from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
    from smartutils.app.plugin.header import HeaderPlugin
    from smartutils.app.plugin.log import LogPlugin
    from smartutils.app.plugin.exception import ExceptionPlugin
    from smartutils.app.factory import ExcJsonResp
    from smartutils.app.main.init_middleware import init_middlewares
    from smartutils.app.const import AppKey

    app = FastAPI(lifespan=lifespan)
    app.state.smartutils_conf_path = conf_path  # noqa

    init_middlewares(app, AppKey.FASTAPI)

    # app.add_middleware(
    #     MiddlewareFactory.get(AppKey.FASTAPI),
    #     plugin=ExceptionPlugin(AppKey.FASTAPI),
    #     req_adapter=RequestAdapterFactory.get(AppKey.FASTAPI),
    #     resp_adapter=ResponseAdapterFactory.get(AppKey.FASTAPI),
    # )
    # app.add_middleware(
    #     MiddlewareFactory.get(AppKey.FASTAPI), plugin=HeaderPlugin(),
    #     req_adapter=RequestAdapterFactory.get(AppKey.FASTAPI),
    #     resp_adapter=ResponseAdapterFactory.get(AppKey.FASTAPI),
    # )
    # app.add_middleware(
    #     MiddlewareFactory.get(AppKey.FASTAPI), plugin=LogPlugin(),
    #     req_adapter=RequestAdapterFactory.get(AppKey.FASTAPI),
    #     resp_adapter=ResponseAdapterFactory.get(AppKey.FASTAPI),
    # )

    @app.exception_handler(RequestValidationError)
    async def _(request: Request, exc: RequestValidationError):
        return ExcJsonResp.handle(exc, AppKey.FASTAPI).response

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
