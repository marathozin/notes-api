"""
Тесты фильтрации заметок по тегам и управления тегами заметок
"""


def test_filter_notes_by_preset_tags(client, auth_headers):
    """Тест фильтрации заметок по предустановленным тегам"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    work_tag = next(tag for tag in tags if tag["name"] == "работа")
    fav_tag = next(tag for tag in tags if tag["name"] == "избранное")

    client.post(
        "/notes",
        headers=headers,
        json={"title": "Рабочая", "content": "...", "tag_ids": [work_tag["id"]]},
    )
    client.post(
        "/notes",
        headers=headers,
        json={"title": "Личная", "content": "...", "tag_ids": [fav_tag["id"]]},
    )

    response = client.get(f"/notes?tag_ids={work_tag['id']}", headers=headers)
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1
    assert notes[0]["title"] == "Рабочая"


def test_filter_notes_by_multiple_tags(client, auth_headers):
    """Тест фильтрации заметок по нескольким тегам"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    work_tag = next(tag for tag in tags if tag["name"] == "работа")
    fav_tag = next(tag for tag in tags if tag["name"] == "избранное")

    client.post(
        "/notes",
        headers=headers,
        json={
            "title": "Важная работа",
            "content": "...",
            "tag_ids": [work_tag["id"], fav_tag["id"]],
        },
    )
    client.post(
        "/notes",
        headers=headers,
        json={"title": "Просто работа", "content": "...", "tag_ids": [work_tag["id"]]},
    )

    response = client.get(
        f"/notes?tag_ids={work_tag['id']},{fav_tag['id']}", headers=headers
    )
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 1


def test_add_tag_to_note(client, auth_headers):
    """Тест добавления тега к заметке"""
    headers = auth_headers()

    # Создание заметки без тегов
    note = client.post(
        "/notes", headers=headers, json={"title": "Заметка", "content": "Контент"}
    ).json()

    # Получение тега
    tags = client.get("/tags").json()
    tag = next(tag for tag in tags if tag["name"] == "избранное")

    # Добавление тега к заметке
    response = client.post(f"/notes/{note['id']}/tags/{tag['id']}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["tags"]) == 1
    assert response.json()["tags"][0]["name"] == "избранное"


def test_add_multiple_tags_to_note(client, auth_headers):
    """Тест добавления нескольких тегов к заметке"""
    headers = auth_headers()

    note = client.post(
        "/notes", headers=headers, json={"title": "Заметка", "content": "Контент"}
    ).json()

    tags = client.get("/tags").json()
    tag1 = next(tag for tag in tags if tag["name"] == "работа")
    tag2 = next(tag for tag in tags if tag["name"] == "избранное")

    client.post(f"/notes/{note['id']}/tags/{tag1['id']}", headers=headers)
    response = client.post(f"/notes/{note['id']}/tags/{tag2['id']}", headers=headers)

    assert response.status_code == 200
    assert len(response.json()["tags"]) == 2


def test_add_duplicate_tag_to_note(client, auth_headers):
    """Тест добавления дублирующегося тега к заметке"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    tag = next(tag for tag in tags if tag["name"] == "работа")

    note = client.post(
        "/notes",
        headers=headers,
        json={"title": "Заметка", "content": "...", "tag_ids": [tag["id"]]},
    ).json()

    response = client.post(f"/notes/{note['id']}/tags/{tag['id']}", headers=headers)
    assert response.status_code == 200
    # Количество тегов не должно увеличиться
    assert len(response.json()["tags"]) == 1


def test_remove_tag_from_note(client, auth_headers):
    """Тест удаления тега из заметки"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    tag = next(tag for tag in tags if tag["name"] == "работа")

    note = client.post(
        "/notes",
        headers=headers,
        json={"title": "Заметка", "content": "...", "tag_ids": [tag["id"]]},
    ).json()

    # Удаление тега
    response = client.delete(f"/notes/{note['id']}/tags/{tag['id']}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["tags"]) == 0


def test_remove_nonexistent_tag_from_note(client, auth_headers):
    """Тест удаления несуществующего тега из заметки"""
    headers = auth_headers()

    note = client.post(
        "/notes", headers=headers, json={"title": "Заметка", "content": "Контент"}
    ).json()

    # Попытка удалить тег, которого нет
    tags = client.get("/tags").json()
    tag = tags[0]
    response = client.delete(f"/notes/{note['id']}/tags/{tag['id']}", headers=headers)

    assert response.status_code == 200
    assert len(response.json()["tags"]) == 0


def test_update_note_tags(client, auth_headers):
    """Тест обновления тегов заметки через PUT"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    tag1 = next(tag for tag in tags if tag["name"] == "работа")
    tag2 = next(tag for tag in tags if tag["name"] == "избранное")
    tag3 = next(tag for tag in tags if tag["name"] == "срочно")

    note = client.post(
        "/notes",
        headers=headers,
        json={"title": "Заметка", "content": "...", "tag_ids": [tag1["id"]]},
    ).json()

    response = client.put(
        f"/notes/{note['id']}",
        headers=headers,
        json={"tag_ids": [tag2["id"], tag3["id"]]},
    )

    assert response.status_code == 200
    assert len(response.json()["tags"]) == 2
    tag_names = [tag["name"] for tag in response.json()["tags"]]
    assert "избранное" in tag_names
    assert "срочно" in tag_names
    assert "работа" not in tag_names


def test_clear_all_tags_from_note(client, auth_headers):
    """Тест удаления всех тегов из заметки"""
    headers = auth_headers()

    tags = client.get("/tags").json()
    tag1 = next(tag for tag in tags if tag["name"] == "работа")
    tag2 = next(tag for tag in tags if tag["name"] == "избранное")

    note = client.post(
        "/notes",
        headers=headers,
        json={
            "title": "Заметка",
            "content": "...",
            "tag_ids": [tag1["id"], tag2["id"]],
        },
    ).json()

    # Удаление всех тегов
    response = client.put(f"/notes/{note['id']}", headers=headers, json={"tag_ids": []})

    assert response.status_code == 200
    assert len(response.json()["tags"]) == 0
