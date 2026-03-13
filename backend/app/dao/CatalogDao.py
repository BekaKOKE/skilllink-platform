import uuid
from typing import Sequence, Optional

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.catalog import Catalog
from backend.app.schemas.CatalogSchema import CatalogFilter


class CatalogDao:

    @staticmethod
    async def create(session: AsyncSession, item) -> Catalog:
        session.add(item)
        await session.flush()
        return item

    @staticmethod
    async def update(session: AsyncSession, item: Catalog, update_data) -> Catalog:
        for field, value in update_data.items():
            setattr(item, field, value)

        await session.flush()
        return item

    @staticmethod
    async def delete(session: AsyncSession, item: Catalog) -> None:
        await session.delete(item)
        await session.flush()

    @staticmethod
    async def get_by_specialist_id(
            session: AsyncSession,
            specialist_id: uuid.UUID,
            filters: CatalogFilter
    ) -> Sequence[Catalog]:
        query = (
            select(Catalog).where(Catalog.specialist_id == specialist_id)
        )
        query = CatalogDao.apply_filters(query, filters)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_all(
            session: AsyncSession,
            filters: CatalogFilter,
            limit: Optional[int] = None,
            offset: Optional[int] = None

    ) -> Sequence[Catalog]:
        query = (
            select(Catalog).order_by(Catalog.specialist_id)
        )
        query = CatalogDao.apply_filters(query, filters)
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    def apply_filters(query: Select, filters: CatalogFilter) -> Select:
        if filters.job_type:
            query = query.where(Catalog.job_type == filters.job_type)

        if filters.price_from:
            query = query.where(Catalog.price >= filters.price_from)

        if filters.price_to:
            query = query.where(Catalog.price <= filters.price_to)

        return query
