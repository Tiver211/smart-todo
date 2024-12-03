import pytest
from app import create_app
from app.extensions import db


@pytest.fixture(scope="module")
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Создает таблицы
            yield client  # Переход к тестам
            db.session.remove()  # Закрывает сессию, но не удаляет таблицы
            db.drop_all()


def test_register_success(client):
    response = client.post('/auth/register', json={
        "login": "new_user",
        "email": "user@gmail.com",
        "password": "secure_password",
        "name": "Test User"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User registered successfully"


def test_register_existing_login(client):
    client.post('/auth/register', json={
        "login": "existing_user",
        "email": "existing@gmail.com",
        "password": "password123"
    })
    response = client.post('/auth/register', json={
        "login": "existing_user",
        "email": "new@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Username already registered"


def test_register_invalid_email(client):
    response = client.post('/auth/register', json={
        "login": "user_with_bad_email",
        "email": "bad_email",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json["error"] == "Invalid email"


def test_login_by_login(client):
    client.post('/auth/register', json={
        "login": "test_user",
        "email": "test@gmail.com",
        "password": "test_password"
    })
    response = client.post('/auth/login', json={
        "login": "test_user",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Login successful"


def test_login_by_email(client):
    client.post('/auth/register', json={
        "login": "test_user",
        "email": "test@gmail.com",
        "password": "test_password"
    })
    response = client.post('/auth/login', json={
        "email": "test@gmail.com",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Login successful"


def test_login_invalid_credentials(client):
    response = client.post('/auth/login', json={
        "login": "unknown_user",
        "password": "wrong_password"
    })
    assert response.status_code == 200
    assert response.json["error"] == "Invalid credentials"


def test_logout_success(client):
    client.post('/auth/register', json={
        "login": "user_to_logout",
        "email": "logout@gmail.com",
        "password": "password123"
    })
    client.post('/auth/login', json={
        "login": "user_to_logout",
        "password": "password123"
    })
    response = client.post('/auth/logout')
    assert response.status_code == 302  # Redirect to login


def test_change_data_success(client):
    client.post('/auth/register', json={
        "login": "changeme_user",
        "email": "changeme@gmail.com",
        "password": "old_password"
    })
    client.post('/auth/login', json={
        "login": "changeme_user",
        "password": "old_password"
    })
    response = client.post('/auth/change_data', json={
        "login": "new_login",
        "email": "new_email@gmail.com",
        "name": "New Name"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Данные успешно обновлены"


def test_change_data_conflict(client):
    client.post('/auth/register', json={
        "login": "user1",
        "email": "user1@gmail.com",
        "password": "password"
    })
    client.post('/auth/register', json={
        "login": "user2",
        "email": "user2@gmail.com",
        "password": "password"
    })
    client.post('/auth/login', json={
        "login": "user1",
        "password": "password"
    })
    response = client.post('/auth/change_data', json={
        "login": "user2"
    })
    assert response.status_code == 200
    assert response.json["error"] == "Логин уже занят"
