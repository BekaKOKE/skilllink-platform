import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from backend.app.db.models.user import User
from backend.app.schemas.UserSchema import UserCreate, UserUpdate
from backend.app.validation.CreateValidation import CreateValidation
from backend.app.dao.UserDao import UserDao

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

class UserService:

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> list[User]:
        result = await UserDao.get_all(session,limit,offset)
        return result

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        result = await UserDao.get_by_id(session, user_id)
        return result

    @staticmethod
    async def get_by_name_surname(session: AsyncSession, name: str, surname: str) -> Optional[User]:
        result = await UserDao.get_by_name_surname(session, name, surname)
        return result

    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
        result = await UserDao.get_by_email(session, email)
        return result

    @staticmethod
    async def get_by_phone(session: AsyncSession, phone: str) -> Optional[User]:
        result = await UserDao.get_by_phone(session, phone)
        return result

    @staticmethod
    async def update(session: AsyncSession, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_none=True)

        if "password" in update_data:
            update_data["hashed_password"] = UserService.hash_password(update_data.pop("password"))

        result = await UserDao.update(session, user, update_data)
        return result

    @staticmethod
    async def delete(session: AsyncSession, user: User) -> None:
        await UserDao.delete(session, user)