from smartutils.app.adapter.abstract import RequestAdapter
from smartutils.app.adapter.aiohttp import AIOHTTPRequestAdapter
from smartutils.app.adapter.django import DjangoRequestAdapter
from smartutils.app.adapter.flask import FlaskRequestAdapter
from smartutils.app.adapter.starlette import StarletteRequestAdapter


def get_adapter(request) -> RequestAdapter:
    mod = type(request).__module__
    if mod.startswith("starlette") or mod.startswith("fastapi"):
        return StarletteRequestAdapter(request)
    elif mod.startswith("flask"):
        return FlaskRequestAdapter(request)
    elif mod.startswith("django"):
        return DjangoRequestAdapter(request)
    elif mod.startswith("aiohttp"):
        return AIOHTTPRequestAdapter(request)
    else:
        raise RuntimeError(f"Unknown request type: {type(request)}")
