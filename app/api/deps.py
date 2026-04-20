import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas import TokenData
from app.db import get_db, models
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from app.services import AuthService


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if AuthService.is_token_revoked(token):
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    stmt = select(models.User).where(models.User.username == token_data.username)
    user = db.execute(stmt).scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Проверка активности пользователя"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user
