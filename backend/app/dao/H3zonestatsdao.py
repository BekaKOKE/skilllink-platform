from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.h3ZoneStats import H3ZoneStats
from backend.app.db.models.order import Order
from backend.app.db.models.specialist import Specialist
from backend.app.db.models.enums import OrderStatus


class H3ZoneStatsDao:

    @staticmethod
    async def get_by_h3_index(
        session: AsyncSession,
        h3_index: str
    ) -> Optional[H3ZoneStats]:
        result = await session.execute(
            select(H3ZoneStats).where(H3ZoneStats.h3_index == h3_index)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[H3ZoneStats]:
        query = (
            select(H3ZoneStats).order_by(H3ZoneStats.h3_index)
        )
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        h3_index: str
    ) -> H3ZoneStats:
        zone = await H3ZoneStatsDao.get_by_h3_index(session, h3_index)
        if zone is None:
            zone = H3ZoneStats(h3_index=h3_index)
            session.add(zone)
            await session.flush()
        return zone

    @staticmethod
    async def recompute_zone(
        session: AsyncSession,
        h3_index: str
    ) -> H3ZoneStats:

        total_result = await session.execute(
            select(func.count(Order.id))
            .join(Specialist, Specialist.id == Order.specialist_id)
            .where(Specialist.h3_index == h3_index)
        )
        total_orders: int = total_result.scalar_one() or 0

        completed_result = await session.execute(
            select(func.count(Order.id))
            .join(Specialist, Specialist.id == Order.specialist_id)
            .where(Specialist.h3_index == h3_index)
            .where(Order.status == OrderStatus.completed)
        )
        completed_orders: int = completed_result.scalar_one() or 0

        avg_result = await session.execute(
            select(func.avg(Order.price))
            .join(Specialist, Specialist.id == Order.specialist_id)
            .where(Specialist.h3_index == h3_index)
        )
        avg_price: float = round(float(avg_result.scalar_one() or 0.0), 2)

        specialists_result = await session.execute(
            select(func.count(Specialist.id))
            .where(Specialist.h3_index == h3_index)
            .where(Specialist.is_active == True)
            .where(Specialist.is_verified == True)
        )
        active_specialists: int = specialists_result.scalar_one() or 0

        zone = await H3ZoneStatsDao.get_or_create(session, h3_index)
        zone.total_orders = total_orders
        zone.completed_orders = completed_orders
        zone.avg_price = avg_price
        zone.active_specialists = active_specialists
        zone.updated_at = datetime.now(timezone.utc)

        await session.flush()
        return zone