import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from backend.app.dao.UserDao import UserDao
from backend.app.db.models.catalog import Catalog
from backend.app.db.models.specialist import Specialist


class SpecialistDao:

    @staticmethod
    async def create(session: AsyncSession, specialist: Specialist) -> Specialist:
        session.add(specialist)
        await session.flush()
        return specialist

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[Specialist]:
        query = (
            select(Specialist)
            .order_by(Specialist.user_id)
        )
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, specialist_id: uuid.UUID) -> Optional[Specialist]:
        result = await session.execute(
            select(Specialist).where(Specialist.id == specialist_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[Specialist]:
        result = await session.execute(
            select(Specialist).where(Specialist.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name_surname(session: AsyncSession, name: str, surname: str) -> Optional[Specialist]:
        user = await UserDao.get_by_name_surname(session, name, surname)
        if not user:
            return None
        return await SpecialistDao.get_by_user_id(session, user.id)

    @staticmethod
    async def update(session: AsyncSession, specialist: Specialist, update_data) -> Specialist:
        for field, value in update_data.items():
            setattr(specialist, field, value)

        await session.flush()
        return specialist

    @staticmethod
    async def deactivate(session: AsyncSession, specialist: Specialist) -> Specialist:
        specialist.is_active = False
        await session.flush()
        return specialist

    @staticmethod
    async def delete(session: AsyncSession, specialist: Specialist) -> None:
        await session.delete(specialist)
        await session.flush()

    @staticmethod
    async def verify(session: AsyncSession, specialist: Specialist) -> Specialist:
        specialist.is_verified = True
        await session.flush()
        return specialist

    @staticmethod
    async def find_specialists_nearby(
            session: AsyncSession,
            neighbor_cells,
            job_type: Optional[str] = None,
            max_price: Optional[int] = None
    ) -> Sequence[Specialist]:
        query = (
            select(Specialist)
            .where(col(Specialist.h3_index).in_(neighbor_cells))
            .where(Specialist.is_verified == True)
            .where(Specialist.is_active == True)
        )
        if job_type:
            query = (
                query
                .join(Catalog, Catalog.specialist_id == Specialist.id)
                .where(Catalog.job_type == job_type)
            )

        if max_price:
            if not job_type:
                query = query.join(Catalog, Catalog.specialist_id == Specialist.id)
            query = query.where(Catalog.price <= max_price)

        result = await session.execute(query)
        return result.scalars().unique().all()
