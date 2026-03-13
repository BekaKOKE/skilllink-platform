import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.models.enums import OrderStatus
from backend.app.db.models.order import Order
from backend.app.db.models.rate import Rate


class RateDao:

    @staticmethod
    async def create(session: AsyncSession, rate: Rate) -> Rate:
        session.add(rate)
        await session.flush()
        return rate

    @staticmethod
    async def get_user_rate(
        session: AsyncSession,
        user_id: uuid.UUID,
        specialist_id: uuid.UUID
    ) -> Rate:
        result = await session.execute(
            select(Rate).where(
                Rate.user_id == user_id,
                Rate.specialist_id == specialist_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_specialist_rates(
        session: AsyncSession,
        specialist_id: uuid.UUID
    ) -> Sequence[Rate]:
        result = await session.execute(
            select(Rate).where(Rate.specialist_id == specialist_id)
        )
        return result.scalars().all()

    @staticmethod
    async def delete(
        session: AsyncSession,
        rate: Rate
    ) -> None:
        await session.delete(rate)
        await session.flush()

    @staticmethod
    async def check_completed_order(
        session: AsyncSession,
        user_id: uuid.UUID,
        specialist_id: uuid.UUID
    ) -> bool:
        result = await session.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.specialist_id == specialist_id,
                Order.status == OrderStatus.completed
            )
        )
        return result.scalar_one_or_none() is not None