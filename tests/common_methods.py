from tests.seed_test import TestingSessionLocal
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_token(data):
    data = {
        "email": data["email"],
        "password": data["password"]
    }

    response = client.post("/login", json=data)

    return response.json()["access_token"]