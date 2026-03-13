import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.models.accreditation import Accreditation


class AccreditationDao:

    @staticmethod
    async def create(session: AsyncSession, accreditation: Accreditation) -> Accreditation:
        session.add(accreditation)
        await session.flush()
        return accreditation

    @staticmethod
    async def delete(session: AsyncSession, accreditation: Accreditation) -> None:
        await session.delete(accreditation)
        await session.flush()

    @staticmethod
    async def get_by_specialist_id(session: AsyncSession, specialist_id: uuid.UUID) -> Sequence[Accreditation]:
        result = await session.execute(
            select(Accreditation).where(Accreditation.specialist_id == specialist_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[Accreditation]:
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0

        query = (
            select(Accreditation)
        )
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()