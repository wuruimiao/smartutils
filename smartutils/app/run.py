import argparse
import uvicorn


def start():
    parser = argparse.ArgumentParser(description="Run app/main")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=80, help="Port to bind")
    parser.add_argument("--reload", action="store_false", help="Enable auto-reload")
    args = parser.parse_args()

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload, workers=1, factory=True)
