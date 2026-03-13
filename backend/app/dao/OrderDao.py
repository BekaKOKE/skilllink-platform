import uuid
from datetime import datetime, timezone
from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.models.enums import OrderStatus
from backend.app.db.models.order import Order

class OrderDao:

    @staticmethod
    async def create(
            session: AsyncSession,
            order: Order
    ) -> Order:
        session.add(order)
        await session.flush()
        return order

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        order_id: uuid.UUID
    ) -> Optional[Order]:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_orders(
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> Sequence[Order]:
        result = await session.execute(
            select(Order)
            .where(Order.is_active == True)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_active_orders(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[Order]:
        query = (
            select(Order)
            .where(Order.is_active == True)
            .where(Order.status == OrderStatus.open)
            .order_by(Order.created_at.desc())
        )
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_specialist_orders(
        session: AsyncSession,
        specialist_id: uuid.UUID
    ) -> Sequence[Order]:
        result = await session.execute(
            select(Order)
            .where(Order.specialist_id == specialist_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id_for_update(
            session: AsyncSession,
            order_id: uuid.UUID
    ) -> Optional[Order]:
        result = await session.execute(
            select(Order).where(Order.id == order_id).with_for_update()
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_specialist_active_order(
            session: AsyncSession,
            specialist_id: uuid.UUID
    ) -> Optional[Order]:
        result = await session.execute(
            select(Order)
            .where(Order.specialist_id == specialist_id)
            .where(Order.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
            session: AsyncSession,
            order: Order,
            update_data
    ) -> Order:
        for field, value in update_data.items():
            setattr(order, field, value)

        await session.flush()
        return order

    @staticmethod
    async def deactivate(session: AsyncSession, order: Order) -> Order:
        order.is_active = False
        await session.flush()
        return order

    @staticmethod
    async def delete(session: AsyncSession, order: Order) -> None:
        await session.delete(order)
        await session.flush()

    @staticmethod
    async def take_order(
        session: AsyncSession,
        order: Order,
        specialist_id: uuid.UUID
    ) -> Order:

        order.specialist_id = specialist_id
        order.status = OrderStatus.in_progress
        await session.flush()
        return order

    @staticmethod
    async def complete_order(session: AsyncSession, order: Order) -> Order:
        order.status = OrderStatus.completed
        order.completed_at = datetime.now(timezone.utc)
        order.is_active = False
        await session.flush()
        return order

    @staticmethod
    async def cancel_order(
        session: AsyncSession,
        order: Order
    ) -> Order:
        order.status = OrderStatus.cancelled
        order.is_active = False
        await session.flush()
        return order