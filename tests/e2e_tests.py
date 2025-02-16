import requests
import uuid

BASE_URL = "http://api:8080"

def random_username(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def authenticate_user(username, password="pass"):
    response = requests.post(f"{BASE_URL}/api/auth/", json={"username": username, "password": password})

    assert response.status_code == 200, f"Ошибка авторизации для {username}: {response.text}"
    return response.json()["token"]

def test_missing_auth_body():
    response = requests.post(f"{BASE_URL}/api/auth/")

    assert response.status_code == 422, f"Ожидался код 422 для отсутствующего тела запроса, получен {response.status_code}"

def test_buy_nonexistent_merch():
    username = random_username("nonexistent")
    token = authenticate_user(username)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/buy/unknown-item", headers=headers)

    assert response.status_code == 404, f"Ожидался код 404 для несуществующего товара, получен {response.status_code}"

def test_insufficient_funds_buy():
    username = random_username("poorBuyer")
    token = authenticate_user(username)
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/api/buy/pen", headers=headers)
    assert response.status_code == 200, f"Первоначальная покупка не удалась: {response.text}"

    response = requests.get(f"{BASE_URL}/api/buy/pink-hoody", headers=headers)
    assert response.status_code == 200, f"Ожидалась успешная покупка товара pink-hoody: {response.text}"

    response = requests.get(f"{BASE_URL}/api/buy/pink-hoody", headers=headers)
    assert response.status_code == 400, f"Ожидался код 400 для недостаточных средств, получен {response.status_code}"

def test_negative_transfer_amount():
    username = random_username("negTransfer")
    token = authenticate_user(username)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/sendCoin", json={"toUser": username, "amount": -50}, headers=headers)

    assert response.status_code == 400, f"Отрицательный перевод должен завершаться ошибкой: {response.text}"

def test_transfer_to_nonexistent_user():
    username = random_username("realSender")
    token = authenticate_user(username)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/sendCoin", json={"toUser": "nonexistent_user", "amount": 100}, headers=headers)

    assert response.status_code == 404, f"Перевод монет несуществующему пользователю должен завершаться ошибкой: {response.text}"

def test_access_without_token():
    response = requests.get(f"{BASE_URL}/api/info")

    assert response.status_code == 401, f"Доступ без токена должен возвращать 401, получен {response.status_code}"

def test_multiple_transactions():
    sender = random_username("multiSender")
    recipient = random_username("multiRecipient")
    token_sender = authenticate_user(sender)
    token_recipient = authenticate_user(recipient)
    headers_sender = {"Authorization": f"Bearer {token_sender}"}
    headers_recipient = {"Authorization": f"Bearer {token_recipient}"}
    
    response = requests.post(f"{BASE_URL}/api/sendCoin", json={"toUser": recipient, "amount": 200}, headers=headers_sender)
    assert response.status_code == 200, f"Первый перевод не удался: {response.text}"
    
    response = requests.get(f"{BASE_URL}/api/buy/t-shirt", headers=headers_sender)
    assert response.status_code == 200, f"Покупка отправителем не удалась: {response.text}"
    
    response = requests.get(f"{BASE_URL}/api/info", headers=headers_sender)
    info_sender = response.json()
    assert isinstance(info_sender.get("coins"), int), "Количество монет должно быть целым числом"
    assert "inventory" in info_sender, "В информации отсутствует инвентарь"
    assert "coinHistory" in info_sender, "В информации отсутствует история операций с монетами"

    response = requests.get(f"{BASE_URL}/api/info", headers=headers_recipient)
    info_recipient = response.json()
    assert info_recipient.get("coins") == 1200, f"Ожидался баланс получателя равный 1200 монет, получено {info_recipient.get('coins')}"

def run_all_tests():
    tests = [
        ("Отсутствует тело запроса авторизации", test_missing_auth_body),
        ("Покупка несуществующего мерча", test_buy_nonexistent_merch),
        ("Недостаточно средств для покупки", test_insufficient_funds_buy),
        ("Отрицательный перевод", test_negative_transfer_amount),
        ("Перевод монет несуществующему пользователю", test_transfer_to_nonexistent_user),
        ("Доступ без токена", test_access_without_token),
        ("Множественные транзакции", test_multiple_transactions),
    ]
    failed = 0
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"[PASS] {test_name}")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {test_name}: {e}")
    if failed == 0:
        print("Все E2E тесты пройдены!")
    else:
        print(f"{failed} тест(ов) не пройдено.")
        exit(1)

if __name__ == "__main__":
    run_all_tests()