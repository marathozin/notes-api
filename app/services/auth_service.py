from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.db import models
from app.schemas import UserCreate
from datetime import timedelta
from app.core import settings, verify_password, get_password_hash, create_access_token


class AuthService:
    @staticmethod
    def register_new_user(db: Session, user_data: UserCreate) -> models.User:
        """Регистрация нового пользователя"""
        stmt = select(models.User).where(
            or_(
                models.User.email == user_data.email,
                models.User.username == user_data.username,
            )
        )
        existing_user = db.execute(stmt).scalars().first()

        if existing_user:
            detail = (
                "Email уже зарегистрирован"
                if existing_user.email == user_data.email
                else "Имя пользователя уже занято"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        hashed_password = get_password_hash(user_data.password)
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """Проверка учетных данных"""
        stmt = select(models.User).where(models.User.username == username)
        user = db.execute(stmt).scalars().first()

        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def login(db: Session, username: str, password: str):
        """Вход в систему и получение JWT токена"""
        user = AuthService.authenticate_user(db, username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
