from pydantic import BaseModel, EmailStr
from uuid import UUID
from backend.app.db.models.enums import UserRole


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: UserRole


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole

    class Config:
        from_attributes = True