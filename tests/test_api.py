"""
Тесты базовых эндпоинтов API
"""
import pytest


@pytest.mark.parametrize("path, expected_status, expected_json", [
    ("/", 200, {"message": "Notes API", "docs": "/docs"}),
    ("/api/v1/", 200, {"version": "1.0",
        "docs": "/docs",
        "status": "running"}),
])
def test_system_endpoints(base_client, path, expected_status, expected_json):
    response = base_client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_json


def test_unauthorized_access(client):
    """Тест доступа без аутентификации"""
    response = client.get("/notes")
    assert response.status_code == 401
