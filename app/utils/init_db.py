"""
Скрипт для инициализации базы данных с предустановленными тегами
"""

from sqlalchemy import select, func
from app.db import SessionLocal, engine, models

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


def init_db():
    """Инициализация базы данных"""
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for tag_data in PRESET_TAGS:
            # Проверка уществует ли тег
            existing_tag = (
                db.execute(
                    select(models.Tag).where(models.Tag.name == tag_data["name"])
                )
                .scalars()
                .first()
            )

            if not existing_tag:
                tag = models.Tag(**tag_data)
                db.add(tag)
                print(f"Добавлен тег: {tag_data['emoji']} {tag_data['name']}")
            else:
                print(f"Тег уже существует: {tag_data['emoji']} {tag_data['name']}")

        db.commit()

        # Вывод статистики
        stmt = select(func.count(models.Tag.id))
        tag_count = db.execute(stmt).scalar()
        print(f"\nДоступно тегов: {tag_count}")

    except Exception as e:
        print(f"\nОшибка при инициализации: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
