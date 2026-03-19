from locust import HttpUser, task, between

class RateLimiterUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def test_token_bucket(self):
        self.client.post(
            "/check-limit/token-bucket",
            params={
                "client_id": f"user_{self.user_id}",
                "capacity": 100,
                "refill_rate": 10.0
            }
        )

    @task(2)
    def test_sliding_window(self):
        self.client.post(
            "/check-limit/sliding-window",
            params={
                "client_id": f"user_{self.user_id}",
                "limit": 100,
                "window_seconds": 60
            }
        )

    @task(1)
    def test_fixed_window(self):
        self.client.post(
            "/check-limit/fixed-window",
            params={
                "client_id": f"user_{self.user_id}",
                "limit": 100,
                "window_seconds": 60
            }
        )

    @property
    def user_id(self):
        return id(self) % 100
