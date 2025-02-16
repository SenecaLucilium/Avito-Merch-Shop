import uuid
import random
from locust import HttpUser, TaskSet, task, between

MERCH_ITEMS = ["t-shirt", "cup", "book", "pen", "powerbank", "hoody", "umbrella", "socks", "wallet", "pink-hoody"]

def random_username(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

class UserBehavior(TaskSet):
    def on_start(self):
        username = random_username("user")
        response = self.client.post("/api/auth/", json={"username": username, "password": "pass"})

        if response.status_code != 200:
            self.interrupt()
        
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(2)
    def buy_merch(self):
        item = random.choice(MERCH_ITEMS)
        self.client.get(f"/api/buy/{item}", headers=self.headers)

    @task(1)
    def send_coin(self):
        recipient = random_username("recipient")
        resp = self.client.post("/api/auth/", json={"username": recipient, "password": "pass"})
        
        if resp.status_code == 200:
            amount = random.randint(10, 200)
            self.client.post("/api/sendCoin", json={"toUser": recipient, "amount": amount}, headers=self.headers)

    @task(1)
    def get_info(self):
        self.client.get("/api/info", headers=self.headers)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 2)