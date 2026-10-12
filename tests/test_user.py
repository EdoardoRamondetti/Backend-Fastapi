from fastapi.testclient import TestClient
from main import app
from database import get_db
from tests.common_methods import override_get_db,get_token
from models import User

client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db

def test_admin_route_as_normal_user():
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.get("/admin-test", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403

def test_admin_route_as_admin():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/admin-test", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(),list)

def test_get_user():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/users/3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == 3

def test_get_user_not_existing():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/users/99", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_get_user_name():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/users/1/name", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Andrea"

def test_get_posts_of_user():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/users/1/posts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_get_posts_of_user_fail():
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.get("/users/99/posts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_add_user():
    newUser = {"name":"edoardo","email":"edoardo@gmail.com","password":"password123"}
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.post("/users", json=newUser,headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["name"] == "edoardo"
    assert response.json()["email"] == "edoardo@gmail.com"
    assert "password_hash" not in response.json()

def test_add_user_existing_email():
    newUser = {"name":"roberto","bio":"","email":"antonio@gmail.com","password":"password123"}
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.post("/users", json=newUser,headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 409

def test_update_user_owner():
    newUser = {"name":"antonio","email":"antonio12@gmail.com","password":"password123"}
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.put("/users/2", json=newUser,headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["email"] == newUser["email"]

def test_update_user_not_owner():
    newUser = {"name":"antonio","email":"luca@gmail.com","password":"password123"}
    token = get_token({"email":"luca@example.com", "password":"password123"})
    response = client.put("/users/2", json=newUser,headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403

def test_update_user_admin():
    newUser = {"name":"antonio","email":"antonio210@gmail.com","role":"user","password":"password123"}
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.put("/users/3", json=newUser,headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["email"] == newUser["email"]

def test_user_delete_himself(db):
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.delete("/users/2",headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    user = db.query(User).filter(User.id == 2).first()
    assert user is None

def test_admin_delete_user(db):
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.delete("/users/2",headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    user = db.query(User).filter(User.id == 2).first()
    assert user is None

def test_admin_delete_admin(db):
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.delete("/users/1",headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403

    user = db.query(User).filter(User.id == 1).first()
    assert user is not None

def test_user_delete_user(db):
    token = get_token({"email":"luca@example.com", "password":"password123"})
    response = client.delete("/users/2",headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403

    user = db.query(User).filter(User.id == 2).first()
    assert user is not None