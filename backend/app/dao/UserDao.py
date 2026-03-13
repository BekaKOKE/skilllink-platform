import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.models.user import User


class UserDao:

    @staticmethod
    async def create(session: AsyncSession, user: User) -> None:
        session.add(user)
        await session.flush()

    @staticmethod
    async def delete(session: AsyncSession, user: User) -> None:
        await session.delete(user)
        await session.flush()


    @staticmethod
    async def update(session: AsyncSession, user: User, update_data) -> User:
        for field, value in update_data.items():
            setattr(user, field, value)

        await session.flush()
        return user

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[User]:
        query = (select(User))
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name_surname(session: AsyncSession, name: str, surname: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.name == name, User.surname == surname)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_phone(session: AsyncSession, phone: str) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()