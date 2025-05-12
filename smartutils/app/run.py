import argparse
import uvicorn

from smartutils.app.fast.app import create_app

# TODO: 兼容多种应用，不限于fastapi


def run():
    parser = argparse.ArgumentParser(description="Run app/main")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=80, help="Port to bind")
    parser.add_argument("--reload", action="store_false", help="Enable auto-reload")
    args = parser.parse_args()

    uvicorn.run(
        create_app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1,
        factory=True,
    )
