"""
Тесты CRUD операций с заметками
"""


def test_create_note(client, auth_headers, sample_note_data):
    """Тест создания заметки"""
    headers = auth_headers()
    response = client.post("/notes", headers=headers, json=sample_note_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_note_data["title"]
    assert data["content"] == sample_note_data["content"]
    assert "id" in data
    assert "created_at" in data


def test_create_note_with_preset_tags(client, auth_headers):
    """Тест создания заметки с предустановленными тегами"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    work_tag = next(tag for tag in tags if tag["name"] == "работа")
    fav_tag = next(tag for tag in tags if tag["name"] == "избранное")

    response = client.post(
        "/notes",
        headers=headers,
        json={
            "title": "Рабочая задача",
            "content": "Важная рабочая задача",
            "tag_ids": [work_tag["id"], fav_tag["id"]],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["tags"]) == 2
    tag_names = [tag["name"] for tag in data["tags"]]
    assert "работа" in tag_names
    assert "избранное" in tag_names


def test_create_note_unauthorized(client, sample_note_data):
    """Тест создания заметки без авторизации"""
    response = client.post("/notes", json=sample_note_data)
    assert response.status_code == 401


def test_get_notes(client, auth_headers, sample_note_data):
    """Тест получения заметок"""
    headers = auth_headers()

    client.post("/notes", headers=headers, json=sample_note_data)

    response = client.get("/notes", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_get_notes_empty(client, auth_headers):
    """Тест получения пустого списка заметок"""
    headers = auth_headers()
    response = client.get("/notes", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_note_by_id(client, auth_headers, sample_note_data):
    """Тест получения заметки по ID"""
    headers = auth_headers()

    create_response = client.post("/notes", headers=headers, json=sample_note_data)
    note_id = create_response.json()["id"]

    response = client.get(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == note_id
    assert response.json()["title"] == sample_note_data["title"]


def test_get_nonexistent_note(client, auth_headers):
    """Тест получения несуществующей заметки"""
    headers = auth_headers()
    response = client.get("/notes/999999", headers=headers)
    assert response.status_code == 404


def test_user_can_only_see_own_notes(client, auth_headers):
    """Тест: пользователь видит только свои заметки"""
    headers1 = auth_headers("user1", "pass123")
    headers2 = auth_headers("user2", "pass456")

    client.post(
        "/notes",
        headers=headers1,
        json={"title": "Заметка пользователя 1", "content": "Контент"},
    )
    client.post(
        "/notes",
        headers=headers2,
        json={"title": "Заметка пользователя 2", "content": "Контент"},
    )

    response1 = client.get("/notes", headers=headers1)
    response2 = client.get("/notes", headers=headers2)

    assert len(response1.json()) == 1
    assert len(response2.json()) == 1
    assert response1.json()[0]["title"] == "Заметка пользователя 1"
    assert response2.json()[0]["title"] == "Заметка пользователя 2"


def test_user_cannot_access_other_user_note(client, auth_headers):
    """Тест: пользователь не может получить чужую заметку"""
    headers1 = auth_headers("user1", "pass123")
    headers2 = auth_headers("user2", "pass456")

    # user1 создает заметку
    create_response = client.post(
        "/notes",
        headers=headers1,
        json={"title": "Заметка user1", "content": "Контент"},
    )
    note_id = create_response.json()["id"]

    # user2 пытается получить заметку user1
    response = client.get(f"/notes/{note_id}", headers=headers2)
    assert response.status_code == 404


def test_update_note(client, auth_headers, sample_note_data):
    """Тест обновления заметки"""
    headers = auth_headers()

    create_response = client.post("/notes", headers=headers, json=sample_note_data)
    note_id = create_response.json()["id"]

    response = client.put(
        f"/notes/{note_id}", headers=headers, json={"title": "Новое название"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Новое название"
    assert response.json()["content"] == sample_note_data["content"]


def test_update_nonexistent_note(client, auth_headers):
    """Тест обновления несуществующей заметки"""
    headers = auth_headers()
    response = client.put(
        "/notes/999999", headers=headers, json={"title": "Новое название"}
    )
    assert response.status_code == 404


def test_delete_note(client, auth_headers, sample_note_data):
    """Тест удаления заметки"""
    headers = auth_headers()

    create_response = client.post("/notes", headers=headers, json=sample_note_data)
    note_id = create_response.json()["id"]

    response = client.delete(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 204

    get_response = client.get(f"/notes/{note_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_nonexistent_note(client, auth_headers):
    """Тест удаления несуществующей заметки"""
    headers = auth_headers()
    response = client.delete("/notes/999999", headers=headers)
    assert response.status_code == 404


def test_search_notes(client, auth_headers):
    """Тест поиска заметок"""
    headers = auth_headers()

    # Создание заметок
    client.post(
        "/notes",
        headers=headers,
        json={"title": "Python разработка", "content": "FastAPI framework"},
    )
    client.post(
        "/notes",
        headers=headers,
        json={"title": "JavaScript код", "content": "React library"},
    )

    # Поиск по слову Python
    response = client.get("/notes/search?query=Python", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any("Python" in note["title"] for note in results)


def test_search_notes_no_results(client, auth_headers):
    """Тест поиска заметок без результатов"""
    headers = auth_headers()
    response = client.get("/notes/search?query=nonexistent", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
