from fastapi import FastAPI

from smartutils.app import AppHook, run


@AppHook.on_startup
async def init_app(app: FastAPI):
    @app.get("/")
    async def root():
        return {"hello": "world"}


if __name__ == "__main__":
    run()
