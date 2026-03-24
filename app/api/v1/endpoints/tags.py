from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas import Tag
from app.services import TagService


router = APIRouter()

@router.get("/", response_model=list[Tag])
def get_tags(db: Session = Depends(get_db)):
    """Получить все доступные теги"""
    return TagService.get_tags(db)