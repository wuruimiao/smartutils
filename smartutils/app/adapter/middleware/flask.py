from smartutils.app.adapter import get_request_adapter, get_response_adapter

__all__ = ["register_plugin"]


def register_plugin(app, plugin):
    from flask import request, g

    @app.before_request
    def before():
        req = get_request_adapter(request)
        g._plugin_req = req
        if hasattr(plugin, "before_request"):
            import asyncio

            asyncio.run(plugin.before_request(req))

    @app.after_request
    def after(response):
        req = getattr(g, "_plugin_req", None)
        if req and hasattr(plugin, "after_request"):
            import asyncio

            asyncio.run(plugin.after_request(req, get_response_adapter(response)))
        return response
