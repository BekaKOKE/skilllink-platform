import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.address import Address


class AddressDao:

    @staticmethod
    async def create(session: AsyncSession, address: Address) -> Address:
        session.add(address)
        await session.flush()
        return address

    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[Address]:
        result = await session.execute(
            select(Address).where(Address.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[Address]:
        query = (
            select(Address)
        )
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def delete(session: AsyncSession, address: Address) -> None:
        await session.delete(address)
        await session.flush()