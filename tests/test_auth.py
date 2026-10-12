from fastapi.testclient import TestClient
from main import app
from tests.common_methods import override_get_db,get_token
from database import get_db

client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db

def test_profile_without_auth():
    response = client.get("/test-auth")

    assert response.status_code == 401

def test_login():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/test-auth", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "andrea@test.com"

def test_login_wrong_password():
    data = {"email":"andrea@test.com", "password":"password"}

    response = client.post("/login", json=data)

    assert response.status_code == 401

def test_login_wrong_email():
    data = {"email":"andrea@gmail.com", "password":"password123"}

    response = client.post("/login", json=data)

    assert response.status_code == 401

def test_signup():
    newUser = {"name":"edoardo","email":"edoardo@gmail.com","role":"user","password":"password123"}
 
    response = client.post("/signup", json=newUser)

    assert response.status_code == 200

def test_signup_existing_email():
    newUser = {"name":"edoardo","email":"antonio@gmail.com","role":"user","password":"password123"}
 
    response = client.post("/signup", json=newUser)

    assert response.status_code == 409   