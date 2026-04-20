from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import models


class TagService:
    @staticmethod
    def get_tags(db: Session):
        """Получить все доступные теги"""
        tags = db.execute(select(models.Tag)).scalars().all()
        return tags
