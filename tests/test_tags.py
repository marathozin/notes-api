"""
Тесты управления тегами
"""


def test_get_preset_tags(client):
    """Тест получения предустановленных тегов"""
    response = client.get("/tags")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) == 9  # 9 предустановленных тегов
    
    tag_names = [tag["name"] for tag in tags]
    assert "работа" in tag_names
    assert "избранное" in tag_names
    assert "срочно" in tag_names