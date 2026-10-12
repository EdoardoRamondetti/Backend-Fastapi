from fastapi.testclient import TestClient
from main import app
from security import decode_token
from tests.common_methods import override_get_db,get_token
from database import get_db
from models import Post

client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db

def test_get_posts_and_user():
    response = client.get("/posts")

    assert response.status_code == 200
    assert len(response.json()) <= 10

def test_get_posts_and_user_with_limit():
    response = client.get("/posts?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_posts_and_user_with_offset():
    response = client.get("/posts?offset=1")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 2

def test_get_posts_and_user_with_wrong_lower_limit():
    response = client.get("/posts?limit=0")

    assert response.status_code == 422

def test_get_posts_and_user_with_wrong_upper_limit():
    response = client.get("/posts?limit=101")

    assert response.status_code == 422

def test_get_posts_and_user_with_wrong_offset():
    response = client.get("/posts?offset=-1")

    assert response.status_code == 422

def test_get_posts_by_user_id():
    response = client.get("/posts?user_id=1")

    assert response.status_code == 200
    assert all(post["user_id"] == 1 for post in response.json())

def test_get_posts_by_user_id_not_existing():
    response = client.get("/posts?user_id=999")

    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_posts_by_wrong_user_id():
    response = client.get("/posts?user_id=abc")

    assert response.status_code == 422

def test_get_posts_by_user_id_with_limit():
    response = client.get("/posts?user_id=1&limit=2")

    assert response.status_code == 200
    assert all(post["user_id"] == 1 for post in response.json())
    assert len(response.json()) == 2

def test_get_posts_with_like():
    response = client.get("/posts?search=python")

    assert response.status_code == 200
    assert all("python" in post["title"].lower() for post in response.json())

def test_get_posts_with_like_case_unsensitive():
    response = client.get("/posts?search=Python")

    assert response.status_code == 200
    assert all("python" in post["title"].lower() for post in response.json())

def test_get_posts_with_like_no_result():
    response = client.get("/posts?search=sport")

    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_posts_with_like_and_user_id():
    response = client.get("/posts?search=python&user_id=2")

    assert response.status_code == 200
    assert all("python" in post["title"].lower() and post["user_id"] == 2 for post in response.json())

def test_get_posts_with_like_and_limit_and_offset():
    response = client.get("/posts?search=python&limit=2&offset=1")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == 7

def test_get_posts_with_sort_and_order():
    response = client.get("/posts?sort=title&order=desc")

    assert response.status_code == 200
    assert response.json()[0]["title"] >= response.json()[-1]["title"]

def test_get_posts_with_sort_and_order_desc():
    response = client.get("/posts?sort=id&order=desc")

    assert response.status_code == 200
    assert response.json()[0]["id"] > response.json()[-1]["id"]

def test_get_posts_with_sort_wrong():
    response = client.get("/posts?sort=password_hash")
    
    assert response.status_code == 422

def test_get_posts_with_sort_and_order_wrong():
    response = client.get("/posts?order=random")
    
    assert response.status_code == 422

def test_get_posts_with_sort_order_user_id_pagination():
    response = client.get("/posts?search=python&limit=2&offset=1&sort=title&order=desc")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == 6
    assert response.json()[0]["title"] >= response.json()[-1]["title"]

def test_exist_poster_after_cancellation():
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.get("/posts/2", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

def test_add_post():
    newPost = {"title":"post2", "content":"questo è un post"}
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    current_user_id = int(decode_token(token)["sub"])
    response = client.post("/posts", json=newPost ,headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["title"] == "post2"
    assert response.json()["content"] == "questo è un post"
    assert response.json()["user_id"] == current_user_id

def test_add_post_without_auth():
    newPost = {"title":"post2", "content":"questo è un post"}
    response = client.post("/posts", json=newPost)

    assert response.status_code == 401

def test_add_post_invalid_token():
    newPost = {"title":"post2", "content":"questo è un post"}
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiaWF0IjoxNzkxMjk0NTk5LCJleHAiOjE3OTEyOTYzOTl9.Pcda-zc3ju1I3XINkdRvJvQG2O7YWyOFkE9oMoJciAA"
    response = client.post("/posts", json=newPost ,headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401

def test_add_post_data():
    newPost = {"title":"post3"}
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.post("/posts", json=newPost ,headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422

def test_add_post_data_length():
    newPost = {"title":"postxK9@pL2#vQ7!mZ4$rT8&nB1*eF6^wY3@cH9!sD5%kR2&jP8#uN4*vX7!qL3$zA6^b"
               + "M9@tF2#gH8&wC5!yR1$kV7^pE4@nJ6&xS9#dQ2!mT5$rZ8^fL3@hB7*wK1!cP4%vN6&gY9#sR2^eA5@uD8!qF3$", "content":"questo è un post generico"}
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.post("/posts", json=newPost ,headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422

def test_get_post_not_existing():
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.get("/posts/10",headers={"Authorization": f"Bearer {token}"} )
    assert response.status_code == 404

def test_update_post():
    newPost = {"title":"post modificato", "content":"nuovo contenuto"}
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    user_id = decode_token(token)["sub"]
    response = client.put("/posts/2",json=newPost,headers={"Authorization": f"Bearer {token}"} )

    assert response.status_code == 200
    assert response.json()["title"] == "post modificato"
    assert response.json()["content"] == "nuovo contenuto"
    assert response.json()["user_id"] == int(user_id)

def test_update_post_not_owner():
    newPost = {"title":"post modificato", "content":"nuovo contenuto"}
    token = get_token({"email":"luca@example.com", "password":"password123"})
    response = client.put("/posts/2",json=newPost,headers={"Authorization": f"Bearer {token}"} )

    assert response.status_code == 403

def test_update_post_admin():
    newPost = {"title":"post modificato da admin", "content":"nuovo contenuto"}
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.put("/posts/2",json=newPost,headers={"Authorization": f"Bearer {token}"} )

    assert response.status_code == 200
    assert response.json()["title"] == newPost["title"]
    assert response.json()["content"] == newPost["content"]
    assert response.json()["user_id"] == 2

def test_delete_post_owner():
    token = get_token({"email":"antonio@gmail.com", "password":"password123"})
    response = client.delete("/posts/2",headers={"Authorization": f"Bearer {token}"} )

    assert response.status_code == 200
    assert response.json()["title"] == "marketing"
    assert response.json()["content"] == "il marketing serve"

    responseGetPost = client.get("/posts/2", headers={"Authorization": f"Bearer {token}"})

    assert responseGetPost.status_code == 404
    assert responseGetPost.text == '{"detail":"Post not found"}'

def test_delete_post_not_owner(db):
    token = get_token({"email":"luca@example.com", "password":"password123"})
    response = client.delete("/posts/2",headers={"Authorization": f"Bearer {token}"} )

    assert response.status_code == 403

    post = db.query(Post).filter(Post.id == 2).first()

    assert post is not None

def test_delete_post_admin(db):
    token = get_token({"email":"andrea@test.com", "password":"password123"})
    response = client.delete("/posts/2",headers={"Authorization": f"Bearer {token}"} )

    assert response.status_code == 200
    assert response.json()["title"] == "marketing"
    assert response.json()["content"] == "il marketing serve"

    post = db.query(Post).filter(Post.id == 2).first()

    assert post is None