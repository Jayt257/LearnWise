from locust import HttpUser, task, between

class LearnwiseUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Executed when a simulated user starts. Login via basic test credentials."""
        # This assumes the testadmin exists, otherwise we just test unauthenticated endpoints
        # For genuine load testing, we'd hit the real server or a dedicated testing env
        with self.client.post("/api/auth/login", json={"email": "admin@test.com", "password": "Admin@1234"}, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.headers = {}
                response.success() # For testing purposes, we don't fail the initial run if testing against an empty DB

    @task(3)
    def check_health(self):
        """Simulate users frequently checking health/status (equivalent to pinging readiness)"""
        self.client.get("/api/health")

    @task(1)
    def view_leaderboard(self):
        """Simulate viewing the public leaderboard"""
        self.client.get("/api/leaderboard/")

    @task(2)
    def get_user_progress(self):
        """Simulate an authenticated user fetching their progress"""
        if self.headers:
            self.client.get("/api/progress/", headers=self.headers)
