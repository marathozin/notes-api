from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.api.deps import get_current_active_user
from app.db import models
from app.services import NoteService
from app.schemas import Note, NoteCreate, NoteUpdate


router = APIRouter()

@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Создать заметку"""
    return NoteService.create_note(db, current_user, note)


@router.get("/", response_model=list[Note])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    tag_ids: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить заметки текущего пользователя с опциональной фильтрацией по тегам
    
    tag_ids: ID тегов через запятую, например: "1,2,3"
    """
    return NoteService.get_notes(db, current_user, skip, limit, tag_ids)


@router.get("/search", response_model=list[Note])
def search_notes(
    query: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Поиск заметок текущего пользователя по названию или содержимому"""
    return NoteService.search_notes(db, current_user, query)


@router.get("/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить заметку по ID"""
    return NoteService.get_note(db, current_user, note_id)


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Обновить заметку"""
    return NoteService.update_note(db, current_user, note_id, note_update)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удалить заметку"""
    return NoteService.delete_note(db, current_user, note_id)


@router.post("/{note_id}/tags/{tag_id}", response_model=Note)
def add_tag_to_note(
    note_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Добавить тег к заметке"""
    return NoteService.add_tag_to_note(db, current_user, note_id, tag_id)


@router.delete("/{note_id}/tags/{tag_id}", response_model=Note)
def remove_tag_from_note(
    note_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удалить тег из заметки"""
    return NoteService.remove_tag_from_note(db, current_user, note_id, tag_id)