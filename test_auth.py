import pytest
from fastapi.testclient import TestClient
from main import app  # Убедитесь, что файл с FastAPI называется main.py

client = TestClient(app)


def test_register():
    response = client.post("/register",
                           json={"username": "john", "email": "john@example.com", "hashed_password": "1234"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}

    # Повторная регистрация существующего пользователя
    response = client.post("/register",
                           json={"username": "john", "email": "john@example.com", "hashed_password": "1234"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


def test_login():
    client.post("/register", json={"username": "john", "email": "john@example.com", "hashed_password": "1234"})

    # Успешная аутентификация
    response = client.post("/token", data={"username": "john", "password": "1234"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Неверный пароль
    response = client.post("/token", data={"username": "john", "password": "wrong"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}


def test_read_users_me():
    client.post("/register", json={"username": "john", "email": "john@example.com", "hashed_password": "1234"})
    response = client.post("/token", data={"username": "john", "password": "1234"})

    token = response.json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"username": "john", "email": "john@example.com", "full_name": None}

    # Попытка доступа без токена
    response = client.get("/users/me")
    assert response.status_code == 401


def test_update_user():
    client.post("/register", json={"username": "john", "email": "john@example.com", "hashed_password": "1234"})
    response = client.post("/token", data={"username": "john", "password": "1234"})

    token = response.json()["access_token"]
    response = client.put("/users/me", json={"username": "john", "email": "john.changed@example.com",
                                             "hashed_password": "newpassword"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User updated successfully"}


def test_logout():
    client.post("/register", json={"username": "john", "email": "john@example.com", "hashed_password": "1234"})
    response = client.post("/token", data={"username": "john", "password": "1234"})

    token = response.json()["access_token"]
    response = client.post("/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User logged out successfully"}

    # Попытка выхода без токена
    response = client.post("/logout")
    assert response.status_code == 401
