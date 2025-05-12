from smartutils.app.adapter import get_request_adapter, get_response_adapter

__all__ = ["DjangoMiddleware"]


class DjangoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.plugin = plugin

    def __call__(self, request):
        req = get_request_adapter(request)
        if hasattr(self.plugin, "before_request"):
            import asyncio

            asyncio.run(self.plugin.before_request(req))
        response = self.get_response(request)
        if hasattr(self.plugin, "after_request"):
            import asyncio

            asyncio.run(self.plugin.after_request(req, get_response_adapter(response)))
        return response
