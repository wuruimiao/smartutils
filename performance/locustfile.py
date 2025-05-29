from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    # 每个用户在请求之间等待的时间区间（单位：秒）
    wait_time = between(0, 0)  # 可以根据需要调整，比如between(0, 0)表示无等待

    @task
    def index(self):
        self.client.get("/")
