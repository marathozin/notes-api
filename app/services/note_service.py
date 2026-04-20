from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.db import models
from app.schemas import NoteCreate, NoteUpdate
from fastapi import HTTPException, status


class NoteService:
    @staticmethod
    def create_note(
        db: Session, current_user: models.User, note: NoteCreate
    ) -> models.User:
        """Создание заметки"""
        # Создание заметки
        db_note = models.Note(
            title=note.title, content=note.content, user_id=current_user.id
        )

        # Добавление тегов
        if note.tag_ids:
            stmt = select(models.Tag).where(models.Tag.id.in_(note.tag_ids))
            tags = db.execute(stmt).scalars().all()
            db_note.tags = tags

        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    @staticmethod
    def get_notes(
        db: Session,
        current_user: models.User,
        skip: int = 0,
        limit: int = 100,
        tag_ids: str | None = None,
    ):
        """Получить заметки текущего пользователя с опциональной фильтрацией по тегам

        tag_ids: ID тегов через запятую, например: "1,2,3"
        """
        stmt = select(models.Note).where(models.Note.user_id == current_user.id)

        # Фильтрация по тегам
        if tag_ids:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(",")]
            stmt = stmt.join(models.Note.tags).where(models.Tag.id.in_(tag_id_list))

        stmt = stmt.offset(skip).limit(limit)
        notes = db.execute(stmt).scalars().all()
        return notes

    @staticmethod
    def get_note(db: Session, current_user: models.User, note_id: int):
        """Получить заметку по ID"""
        note = (
            db.execute(
                select(models.Note).where(
                    models.Note.id == note_id, models.Note.user_id == current_user.id
                )
            )
            .scalars()
            .first()
        )

        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заметка с ID {note_id} не найдена",
            )
        return note

    @staticmethod
    def update_note(
        db: Session, current_user: models.User, note_id: int, note_update: NoteUpdate
    ):
        """Обновить заметку"""
        note = (
            db.execute(
                select(models.Note).where(
                    models.Note.id == note_id, models.Note.user_id == current_user.id
                )
            )
            .scalars()
            .first()
        )

        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заметка с ID {note_id} не найдена",
            )

        # Обновление полей
        update_data = note_update.model_dump(exclude_unset=True, exclude={"tag_ids"})
        for key, value in update_data.items():
            setattr(note, key, value)

        # Обновление тегов
        if note_update.tag_ids is not None:
            stmt = select(models.Tag).where(models.Tag.id.in_(note_update.tag_ids))
            tags = db.execute(stmt).scalars().all()
            note.tags = tags

        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def delete_note(db: Session, current_user: models.User, note_id: int):
        """Удалить заметку"""
        note = (
            db.execute(
                select(models.Note).where(
                    models.Note.id == note_id, models.Note.user_id == current_user.id
                )
            )
            .scalars()
            .first()
        )

        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заметка с ID {note_id} не найдена",
            )

        db.delete(note)
        db.commit()
        return None

    @staticmethod
    def search_notes(db: Session, current_user: models.User, query: str):
        """Поиск заметок текущего пользователя по названию или содержимому"""
        # Подготавливаем поисковый запрос для поиска подстроки
        search_query = f"%{query}%"

        stmt = select(models.Note).where(
            models.Note.user_id == current_user.id,
            or_(
                models.Note.title.ilike(search_query),
                models.Note.content.ilike(search_query),
            ),
        )

        notes = db.execute(stmt).scalars().all()
        return notes

    @staticmethod
    def add_tag_to_note(
        db: Session, current_user: models.User, note_id: int, tag_id: int
    ):
        """Добавить тег к заметке"""
        note = (
            db.execute(
                select(models.Note).where(
                    models.Note.id == note_id, models.Note.user_id == current_user.id
                )
            )
            .scalars()
            .first()
        )

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заметка с ID {note_id} не найдена",
            )

        stmt = select(models.Tag).where(models.Tag.id == tag_id)
        tag = db.execute(stmt).scalars().first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тег с ID {tag_id} не найден",
            )

        if tag not in note.tags:
            note.tags.append(tag)
            db.commit()
            db.refresh(note)

        return note

    @staticmethod
    def remove_tag_from_note(
        db: Session, current_user: models.User, note_id: int, tag_id: int
    ):
        """Удалить тег из заметки"""
        note = (
            db.execute(
                select(models.Note).where(
                    models.Note.id == note_id, models.Note.user_id == current_user.id
                )
            )
            .scalars()
            .first()
        )

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заметка с ID {note_id} не найдена",
            )
        stmt = select(models.Tag).where(models.Tag.id == tag_id)
        tag = db.execute(stmt).scalars().first()
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тег с ID {tag_id} не найден",
            )
        if tag in note.tags:
            note.tags.remove(tag)
            db.commit()
            db.refresh(note)

        return note
