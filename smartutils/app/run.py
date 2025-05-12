import argparse

import uvicorn

from smartutils.app.const import AppKey


# TODO: 兼容多种应用，不限于fastapi


def run():
    parser = argparse.ArgumentParser(description="Run app/main")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=80, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument(
        "--app",
        type=str,
        default=AppKey.FASTAPI.value,
        choices=AppKey.list(),
        help=f"App type, choices: {AppKey.list()}",
    )
    args = parser.parse_args()

    uvicorn.run(
        f"smartutils.app.app.{args.app}:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1,
        factory=True,
    )
