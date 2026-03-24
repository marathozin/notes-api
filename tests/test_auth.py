"""
Тесты аутентификации и управления пользователями
"""


def test_register_user(client):
    """Тест регистрации пользователя"""
    print([route.path for route in client.app.routes])
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "pass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate_email(client):
    """Тест регистрации с дублирующимся email"""
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@test.com",
            "username": "user1",
            "password": "pass123"
        }
    )
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@test.com",
            "username": "user2",
            "password": "pass123"
        }
    )
    assert response.status_code == 400


def test_register_duplicate_username(client):
    """Тест регистрации с дублирующимся username"""
    client.post(
        "/auth/register",
        json={
            "email": "user1@test.com",
            "username": "sameuser",
            "password": "pass123"
        }
    )
    response = client.post(
        "/auth/register",
        json={
            "email": "user2@test.com",
            "username": "sameuser",
            "password": "pass123"
        }
    )
    assert response.status_code == 400


def test_login(client):
    """Тест входа в систему"""
    # Регистрация
    client.post(
        "/auth/register",
        json={
            "email": "login@test.com",
            "username": "loginuser",
            "password": "pass123"
        }
    )
    # Логин
    response = client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Тест входа с неверным паролем"""
    client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "correct"
        }
    )
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Тест входа несуществующего пользователя"""
    response = client.post(
        "/auth/token",
        data={"username": "nonexistent", "password": "pass123"}
    )
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Тест получения информации о текущем пользователе"""
    headers = auth_headers()
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@test.com"


def test_get_current_user_invalid_token(client):
    """Тест получения пользователя с невалидным токеном"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
