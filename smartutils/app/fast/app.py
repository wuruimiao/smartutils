from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    await init()

    from smartutils.config import get_config
    from smartutils.ID import SnowflakeGenerator

    conf = get_config()
    app.state.gen = SnowflakeGenerator(instance=conf.project.id)

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description
    app.debug = conf.project.debug
    if not conf.project.debug:
        app.docs_url = None

    yield

    from smartutils.log import logger

    logger.info(f"shutdown start close")
    from smartutils import release

    await release()
    logger.info(f"shutdown all closed")


def create_app():
    from smartutils.ret import ResponseModel
    from smartutils.app.adapter.middleware.starletee import StarletteMiddleware
    from smartutils.app.plugin.header import HeaderPlugin
    from smartutils.app.plugin.log import LogPlugin

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(StarletteMiddleware, plugin=HeaderPlugin())
    app.add_middleware(StarletteMiddleware, plugin=LogPlugin())

    @app.get("/")
    def root() -> ResponseModel:
        return ResponseModel()

    @app.get("/healthy")
    def healthy() -> ResponseModel:
        return ResponseModel()

    return app
