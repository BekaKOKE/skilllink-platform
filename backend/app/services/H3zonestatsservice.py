import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dao.H3zonestatsdao import H3ZoneStatsDao
from backend.app.dao.SpecialistDao import SpecialistDao
from backend.app.db.models.h3ZoneStats import H3ZoneStats
from backend.app.db.models.order import Order
from backend.app.db.models.specialist import Specialist


class H3ZoneStatsService:

    @staticmethod
    async def get_by_h3_index(
        session: AsyncSession,
        h3_index: str
    ) -> Optional[H3ZoneStats]:
        return await H3ZoneStatsDao.get_by_h3_index(session, h3_index)

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[H3ZoneStats]:
        return await H3ZoneStatsDao.get_all(session, limit, offset)

    @staticmethod
    async def on_order_created(
        session: AsyncSession,
        order: Order
    ) -> None:
        pass

    @staticmethod
    async def on_order_taken(
        session: AsyncSession,
        order: Order,
        specialist_id: uuid.UUID
    ) -> None:
        h3_index = await H3ZoneStatsService._resolve_specialist_h3(session, specialist_id)
        if h3_index:
            await H3ZoneStatsDao.recompute_zone(session, h3_index)

    @staticmethod
    async def on_order_completed(
        session: AsyncSession,
        order: Order
    ) -> None:
        if order.specialist_id:
            h3_index = await H3ZoneStatsService._resolve_specialist_h3(session, order.specialist_id)
            if h3_index:
                await H3ZoneStatsDao.recompute_zone(session, h3_index)

    @staticmethod
    async def on_order_cancelled(
        session: AsyncSession,
        order: Order
    ) -> None:
        if order.specialist_id:
            h3_index = await H3ZoneStatsService._resolve_specialist_h3(session, order.specialist_id)
            if h3_index:
                await H3ZoneStatsDao.recompute_zone(session, h3_index)

    @staticmethod
    async def on_specialist_created(
        session: AsyncSession,
        specialist: Specialist
    ) -> None:
        if specialist.h3_index:
            await H3ZoneStatsDao.recompute_zone(session, specialist.h3_index)

    @staticmethod
    async def on_specialist_deactivated(
        session: AsyncSession,
        specialist: Specialist
    ) -> None:
        if specialist.h3_index:
            await H3ZoneStatsDao.recompute_zone(session, specialist.h3_index)

    @staticmethod
    async def on_specialist_deleted(
        session: AsyncSession,
        h3_index: Optional[str]
    ) -> None:
        if h3_index:
            await H3ZoneStatsDao.recompute_zone(session, h3_index)

    @staticmethod
    async def on_specialist_verified(
        session: AsyncSession,
        specialist: Specialist
    ) -> None:
        if specialist.h3_index:
            await H3ZoneStatsDao.recompute_zone(session, specialist.h3_index)

    @staticmethod
    async def on_specialist_h3_changed(
        session: AsyncSession,
        old_h3_index: Optional[str],
        new_h3_index: str
    ) -> None:
        if old_h3_index and old_h3_index != new_h3_index:
            await H3ZoneStatsDao.recompute_zone(session, old_h3_index)
        await H3ZoneStatsDao.recompute_zone(session, new_h3_index)

    @staticmethod
    async def _resolve_specialist_h3(
        session: AsyncSession,
        specialist_id: uuid.UUID
    ) -> Optional[str]:
        specialist = await SpecialistDao.get_by_id(session, specialist_id)
        if specialist:
            return specialist.h3_index
        return None