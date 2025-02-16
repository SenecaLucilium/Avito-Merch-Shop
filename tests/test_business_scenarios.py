import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def random_username(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def get_auth_token(username: str, password: str):
    response = client.post("/api/auth/", json={"username": username, "password": password})
    assert response.status_code == 200, "Auth failed for user: " + username
    return response.json()["token"]

def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}

# Тесты

def test_auth_creates_user_and_gets_token():
    username = random_username("user")

    response = client.post("/api/auth/", json={"username": username, "password": "pass1"})
    assert response.status_code == 200

    data = response.json()
    assert "token" in data

def test_buy_merch():
    username = random_username("buyer")
    token = get_auth_token(username, "pass")
    headers = auth_headers(token)
    
    response = client.get("/api/buy/pink-hoody", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["purchased_item"] == "pink-hoody"
    assert data["remaining_coins"] == 500

    response = client.get("/api/buy/pen", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["purchased_item"] == "pen"
    assert data["remaining_coins"] == 490

def test_send_coin():
    sender_username = random_username("sender")
    recipient_username = random_username("recipient")
    token_sender = get_auth_token(sender_username, "pass")
    token_recipient = get_auth_token(recipient_username, "pass")
    headers_sender = auth_headers(token_sender)

    response = client.post("/api/sendCoin", json={"toUser": recipient_username, "amount": 200}, headers=headers_sender)
    assert response.status_code == 200

    data = response.json()
    assert data["sender_balance"] == 800
    assert data["recipient_balance"] == 1200

def test_get_info():
    username = random_username("infoUser")
    token = get_auth_token(username, "pass")
    headers = auth_headers(token)
    
    response = client.get("/api/buy/t-shirt", headers=headers)
    assert response.status_code == 200
    
    response = client.get("/api/info", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "coins" in data
    assert isinstance(data["coins"], int)
    assert "inventory" in data
    assert isinstance(data["inventory"], list)
    assert "coinHistory" in data

    history = data["coinHistory"]
    assert "received" in history
    assert "sent" in history

def test_buy_merch_insufficient_funds():
    username = random_username("poorBuyer")
    token = get_auth_token(username, "pass")
    headers = auth_headers(token)

    response = client.get("/api/buy/pink-hoody", headers=headers)
    assert response.status_code == 200

    response = client.get("/api/buy/pink-hoody", headers=headers)
    assert response.status_code == 200

    response = client.get("/api/buy/pen", headers=headers)
    assert response.status_code == 400

def test_send_coin_negative_amount():
    sender_username = random_username("negSender")
    recipient_username = random_username("negRecipient")
    token_sender = get_auth_token(sender_username, "pass")
    headers_sender = auth_headers(token_sender)

    response = client.post("/api/sendCoin", json={"toUser": recipient_username, "amount": -50}, headers=headers_sender)
    assert response.status_code == 400

def test_send_coin_to_nonexistent_user():
    sender_username = random_username("realSender")
    token_sender = get_auth_token(sender_username, "pass")
    headers_sender = auth_headers(token_sender)
    
    response = client.post("/api/sendCoin", json={"toUser": "nonexistent_user", "amount": 100}, headers=headers_sender)
    assert response.status_code == 404

def test_auth_without_body():
    response = client.post("/api/auth/")
    assert response.status_code == 422

def test_access_without_token():
    response = client.get("/api/info")
    assert response.status_code == 401