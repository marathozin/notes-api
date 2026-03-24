from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db, models
from app.main import app
import pytest

# Тестовая база данных
engine = create_engine("postgresql+psycopg://postgres:1234@localhost/test")
TestingSessionLocal = sessionmaker(bind=engine)

# Предустановленные теги с emoji
PRESET_TAGS = [
    {"name": "работа", "emoji": "💼"},
    {"name": "избранное", "emoji": "⭐"},
    {"name": "срочно", "emoji": "🔥"},
    {"name": "идеи", "emoji": "💡"},
    {"name": "проект", "emoji": "📁"},
    {"name": "покупки", "emoji": "🛒"},
    {"name": "здоровье", "emoji": "❤️"},
    {"name": "учеба", "emoji": "📚"},
    {"name": "путешествие", "emoji": "✈️"},
]


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Создание и очистка базы данных перед каждым тестом"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        for tag_data in PRESET_TAGS:
            # Проверяем, существует ли тег
            existing_tag = db.execute(select(models.Tag).where(
                models.Tag.name == tag_data["name"]
            )).scalars().first()
            
            if not existing_tag:
                tag = models.Tag(**tag_data)
                db.add(tag)
        
        db.commit()
    finally:
        db.close()
    yield
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """Fixture для TestClient"""
    return TestClient(app, base_url="http://testserver/api/v1")

@pytest.fixture
def base_client():
    return TestClient(app, base_url="http://testserver")

@pytest.fixture
def get_auth_token(client):
    """Fixture для получения токена авторизации"""
    def _get_token(username="testuser", password="testpass"):
        # Регистрация
        client.post(
            "/auth/register",
            json={
                "email": f"{username}@test.com",
                "username": username,
                "password": password
            }
        )
        # Логин
        response = client.post(
            "/auth/token",
            data={"username": username, "password": password}
        )
        return response.json()["access_token"]
    
    return _get_token


@pytest.fixture
def auth_headers(get_auth_token):
    """Fixture для получения headers с токеном авторизации"""
    def _headers(username="testuser", password="testpass"):
        token = get_auth_token(username, password)
        return {"Authorization": f"Bearer {token}"}
    return _headers


@pytest.fixture
def sample_note_data():
    """Fixture с примером данных заметки"""
    return {
        "title": "Тестовая заметка",
        "content": "Это содержимое тестовой заметки",
        "tag_ids": []
    }