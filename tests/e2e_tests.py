import time
import requests
import uuid

BASE_URL = "http://api:8080"

def random_username(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def authenticate_user(username, password="pass"):
    response = requests.post(f"{BASE_URL}/api/auth/", json={"username": username, "password": password})
    assert response.status_code == 200, f"Auth failed for {username}: {response.text}"
    return response.json()["token"]

def test_e2e_merch_purchase():
    username = random_username("merchBuyer")
    token = authenticate_user(username)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/buy/pink-hoody", headers=headers)
    assert response.status_code == 200, f"Failed to purchase pink-hoody: {response.text}"
    data = response.json()
    assert data.get("purchased_item") == "pink-hoody", "Purchased item mismatch"
    
    response = requests.get(f"{BASE_URL}/api/info", headers=headers)
    assert response.status_code == 200, f"Failed to get info: {response.text}"
    data = response.json()
    assert data.get("coins") == 500, f"Expected coins=500 but got {data.get('coins')}"
    inventory = data.get("inventory", [])
    assert any(item["type"] == "pink-hoody" for item in inventory), "pink-hoody missing from inventory"

def test_e2e_transfer_coin():
    sender_username = random_username("sender")
    recipient_username = random_username("recipient")
    token_sender = authenticate_user(sender_username)
    token_recipient = authenticate_user(recipient_username)
    headers_sender = {"Authorization": f"Bearer {token_sender}"}
    headers_recipient = {"Authorization": f"Bearer {token_recipient}"}
    
    response = requests.post(f"{BASE_URL}/api/sendCoin", json={"toUser": recipient_username, "amount": 300}, headers=headers_sender)
    assert response.status_code == 200, f"Failed coin transfer: {response.text}"
    data = response.json()
    assert data.get("sender_balance") == 700, f"Sender balance expected to be 700, got {data.get('sender_balance')}"
    
    response = requests.get(f"{BASE_URL}/api/info", headers=headers_recipient)
    assert response.status_code == 200, f"Failed to get recipient info: {response.text}"
    data = response.json()
    assert data.get("coins") == 1300, f"Recipient balance expected to be 1300, got {data.get('coins')}"

if __name__ == "__main__":
    test_e2e_merch_purchase()
    test_e2e_transfer_coin()
    print("Integration/E2E tests passed!")