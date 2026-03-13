import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dao.SpecialistDao import SpecialistDao
from backend.app.db.models.order import Order
from backend.app.db.models.enums import OrderStatus
from backend.app.exceptions.NotFoundException import NotFoundException
from backend.app.schemas.OrderSchema import OrderCreate, OrderUpdate
from backend.app.dao.OrderDao import OrderDao
from backend.app.services.H3zonestatsservice import H3ZoneStatsService
from backend.app.validation.OrderValidation import OrderValidation

class OrderService:

    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: uuid.UUID,
        data: OrderCreate
    ) -> Order:
        order = Order(
            user_id=user_id,
            **data.model_dump()
        )
        if order.specialist_id:
            specialist = await SpecialistDao.get_by_id(session, order.specialist_id)
            if specialist is None:
                raise NotFoundException("Specialist not found")
            order.status = OrderStatus.in_progress
        result = await OrderDao.create(session, order)
        await H3ZoneStatsService.on_order_created(session, result)
        return result

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        order_id: uuid.UUID
    ) -> Optional[Order]:
        result = await OrderDao.get_by_id(session, order_id)
        return result

    @staticmethod
    async def get_user_orders(
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> list[Order]:
        result = await OrderDao.get_user_orders(session, user_id)
        return result

    @staticmethod
    async def get_active_orders(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> list[Order]:
        result = await OrderDao.get_active_orders(session,limit,offset)
        return result

    @staticmethod
    async def get_specialist_orders(
        session: AsyncSession,
        specialist_id: uuid.UUID
    ) -> list[Order]:
        result = await OrderDao.get_specialist_orders(session, specialist_id)
        return result

    @staticmethod
    async def update(
        session: AsyncSession,
        order: Order,
        data: OrderUpdate
    ) -> Order:
        update_data = data.model_dump(exclude_none=True)
        OrderValidation.update_validation(order, update_data)
        result = await OrderDao.update(session, order, update_data)
        return result

    @staticmethod
    async def deactivate(session: AsyncSession, order: Order) -> Order:
        OrderValidation.deactivate_validation(order)
        result = await OrderDao.deactivate(session, order)
        return result

    @staticmethod
    async def delete(session: AsyncSession, order: Order) -> None:
        OrderValidation.delete_validation(order)
        await OrderDao.delete(session, order)

    @staticmethod
    async def take_order(
        session: AsyncSession,
        order_id: uuid.UUID,
        specialist_id: uuid.UUID
    ) -> Order:
        order = await OrderDao.get_by_id_for_update(session, order_id)
        if order is None:
            raise NotFoundException("Order not found")

        specialist = await SpecialistDao.get_by_id(session, specialist_id)
        specialist_order = await OrderDao.get_specialist_active_order(session, specialist_id)
        OrderValidation.take_validation(order, specialist, specialist_order)

        result = await OrderDao.take_order(session, order, specialist_id)
        await H3ZoneStatsService.on_order_taken(session, result, specialist_id)
        return result

    @staticmethod
    async def complete_order(
        session: AsyncSession,
        order: Order,
        user_id: uuid.UUID
    ) -> Order:
        OrderValidation.complete_validation(order, user_id)
        result = await OrderDao.complete_order(session, order)
        await H3ZoneStatsService.on_order_completed(session, result)
        return result

    @staticmethod
    async def cancel_order(
        session: AsyncSession,
        order: Order,
        user_id: uuid.UUID
    ) -> Order:
        OrderValidation.cancel_validation(order, user_id)
        result = await OrderDao.cancel_order(session, order)
        await H3ZoneStatsService.on_order_cancelled(session, result)
        return result