from smartutils.app.adapter.req.abstract import RequestAdapter

__all__ = ["TornadoRequestAdapter"]


class TornadoRequestAdapter(RequestAdapter):
    @property
    def headers(self) -> dict:
        # Tornado request.headers 是 HTTPHeaders（dict-like）
        return self.request.headers

    @property
    def query_params(self) -> dict:
        # Tornado request.arguments 是 dict，值为 list
        # 常用 get_argument/get_query_argument 取参数
        # 这里可返回单值版
        return {
            k: v[0].decode("utf-8") if v else ""
            for k, v in self.request.query_arguments.items()
        }

    @property
    def client_host(self) -> str:
        # Tornado request.remote_ip
        return self.request.remote_ip

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def url(self) -> str:
        return self.request.full_url()

    def gen_trace_id(self) -> str:  # noqa
        pass
