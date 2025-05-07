from contextlib import asynccontextmanager
from typing import Callable, Awaitable

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    await init()

    from smartutils.config import get_config, ConfKeys
    from smartutils.ID import IDGen

    import logging

    logging.getLogger("uvicorn.access").disabled = True

    conf = get_config()

    IDGen.init(conf=conf.get(ConfKeys.INSTANCE))

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.project.debug
    if not conf.project.debug:
        app.docs_url = None

    await app.state.smartutils_custom_app(app)

    yield

    from smartutils.log import logger

    logger.info("shutdown start close")
    from smartutils.infra import release

    await release()
    logger.info("shutdown all closed")


def create_app(custom_app: Callable[[FastAPI], Awaitable]):
    from smartutils.ret import ResponseModel
    from smartutils.app.adapter.middleware.starletee import StarletteMiddleware
    from smartutils.app.plugin.header import HeaderPlugin
    from smartutils.app.plugin.log import LogPlugin

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(StarletteMiddleware, plugin=LogPlugin())
    app.add_middleware(StarletteMiddleware, plugin=HeaderPlugin())

    @app.get("/")
    def root() -> ResponseModel:
        return ResponseModel()

    @app.get("/healthy")
    def healthy() -> ResponseModel:
        return ResponseModel()

    app.state.smartutils_custom_app = custom_app

    return app
