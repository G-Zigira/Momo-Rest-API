import sys
sys.path.insert(0, "./")
import time
import threading
import requests
import json
from http.server import HTTPServer
from server import MoMoHandler


BASE_URL = "http://localhost:8081"
AUTH_ADMIN = ("admin", "momo2024")
AUTH_USER = ("user1", "1abcd")


def start_server():
    server = HTTPServer(("localhost", 8081), MoMoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(1)  # Give the server a moment to start
    return server

server = start_server()

def test_get_transactions_admin():
    response = requests.get(f"{BASE_URL}/transactions", auth=AUTH_ADMIN)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data["transactions"], list), f"Expected list of transactions, got {type(data)}"

def test_get_transactions_user():
    response = requests.get(f"{BASE_URL}/transactions", auth=AUTH_USER)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data["transactions"], list), f"Expected list of transactions, got {type(data)}"

def test_get_transactions_no_auth():
    response = requests.get(f"{BASE_URL}/transactions")
    assert response.status_code == 401, f"Expected 401 for no auth, got {response.status_code}"

def test_get_transaction_by_id():
    response = requests.get(f"{BASE_URL}/transactions/1", auth=AUTH_ADMIN)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["id"] == 1

def test_get_transaction_invalid_id():
    response = requests.get(f"{BASE_URL}/transactions/99999", auth=AUTH_ADMIN)
    assert response.status_code == 404, f"Expected 404 for invalid id, got {response.status_code}"

def test_post_transaction_admin():
   response = requests.post(f"{BASE_URL}/transactions", auth=AUTH_ADMIN, json={
       
       "amount": 5000.0,
         "transaction_type": "incoming",
            "party": "Test User ",
   })
   assert response.status_code == 201, f"Expected 201, got {response.status_code}"
   data = response.json()
   assert data["amount"] == 5000.0

def test_post_transaction_user():
    response = requests.post(f"{BASE_URL}/transactions", auth=AUTH_USER, json={
        "amount": 1000.0,
        "transaction_type": "outgoing",
        "party": "Test User ",
    })
    assert response.status_code == 201, f"Expected 201 for user role, got {response.status_code}"

def test_post_transaction_missing_fields():
    response = requests.post(f"{BASE_URL}/transactions", auth=AUTH_ADMIN, json={
        "amount": 5000.0,
    })
    assert response.status_code == 422, f"Expected 422 for missing fields, got {response.status_code}"

def test_put_transaction_admin():
    response = requests.put(f"{BASE_URL}/transactions/1", auth=AUTH_ADMIN, json={
        "amount": 2000.0,
        "transaction_type": "incoming",
        "party": "Updated User ",
    })
    assert response.status_code == 200, f"Expected 200 for admin update, got {response.status_code}"

def test_put_transaction_user_forbidden():
    response = requests.put(f"{BASE_URL}/transactions/1", auth=AUTH_USER, json={
        "amount": 2000.0,
        "transaction_type": "incoming",
        "party": "Updated User ",
    })
    assert response.status_code == 403, f"Expected 403 for user update, got {response.status_code}"

def test_delete_transaction_admin():
    response = requests.delete(f"{BASE_URL}/transactions/1", auth=AUTH_ADMIN)
    assert response.status_code == 200, f"Expected 200 for admin delete, got {response.status_code}"

def test_delete_transaction_user_forbidden():
    response = requests.delete(f"{BASE_URL}/transactions/2", auth=AUTH_USER)
    assert response.status_code == 403, f"Expected 403 for user delete, got {response.status_code}"






