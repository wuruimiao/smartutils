from smartutils.app.adapter import get_request_adapter, get_response_adapter


@web.middleware
async def aiohttp_middleware(request, handler):
    req = get_request_adapter(request)
    await plugin.before_request(req)
    response = await handler(request)
    await plugin.after_request(req, get_response_adapter(response))
    return response
