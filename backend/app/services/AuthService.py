from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from backend.app.dao.UserDao import UserDao
from backend.app.db.models.user import User
from backend.app.core.Security import hash_password, verify_password, create_access_token
from backend.app.schemas.UserSchema import UserCreate
from backend.app.services.UserService import UserService
from backend.app.validation.CreateValidation import CreateValidation


class AuthService:

    @staticmethod
    async def register(session: AsyncSession, data: UserCreate) -> User:
        await CreateValidation.is_valid_user(session, data)

        user = User(
            **data.model_dump(exclude={"password"}),
            hashed_password=hash_password(data.password)
        )

        await UserDao.create(session, user)
        return user

    @staticmethod
    async def login(session: AsyncSession, email: str, password: str):
        user = await UserService.get_by_email(session, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        token = create_access_token({"sub": str(user.id)})
        return token