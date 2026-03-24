from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {
        'from_attributes': True
    }
        

class UserInDB(User):
    hashed_password: str