from pydantic import BaseModel, Field
from datetime import datetime
from .tag import Tag
from .user import User


class NoteBase(BaseModel):
    title: str = Field(
        ..., min_length=1, max_length=200, description="Название заметки"
    )
    content: str = Field(..., min_length=1, description="Содержимое заметки")


class NoteCreate(NoteBase):
    tag_ids: list[int] | None = Field(default=[], description="ID тегов для заметки")


class NoteUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)
    tag_ids: list[int] | None = None


class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None
    tags: list[Tag] = []

    model_config = {"from_attributes": True}


class NoteWithOwner(Note):
    owner: User
