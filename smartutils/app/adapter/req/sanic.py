from smartutils.app.adapter.req.abstract import RequestAdapter


class SanicRequestAdapter(RequestAdapter):
    @property
    def headers(self) -> dict:
        # Sanic request.headers 是 CIMultiDict，支持 dict 行为
        return self.request.headers

    @property
    def query_params(self) -> dict:
        # Sanic request.args 是 MultiDict，支持 dict 行为
        return self.request.args

    @property
    def client_host(self) -> str:
        # Sanic request.remote_addr 是客户端 IP
        return self.request.remote_addr

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def url(self) -> str:
        # Sanic 没有完整 url 属性，可拼接
        return str(self.request.url)

    def gen_trace_id(self) -> str:
        pass
