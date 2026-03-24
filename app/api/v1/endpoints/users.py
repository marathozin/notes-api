from fastapi import APIRouter, Depends
from app import schemas
from app.db import models
from app.api.deps import get_current_active_user


router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе"""
    return current_user