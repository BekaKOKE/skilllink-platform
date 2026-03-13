import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dao.OrderDao import OrderDao
from backend.app.dao.SpecialistDao import SpecialistDao
from backend.app.db.models.message import Message
from backend.app.exceptions.NotFoundException import NotFoundException
from backend.app.exceptions.ValidationException import ValidationException
from backend.app.schemas.MessageSchema import MessageCreate
from backend.app.dao.MessageDao import MessageDao

class MessageService:

    @staticmethod
    async def create(
        session: AsyncSession,
        order_id: uuid.UUID,
        sender_id: uuid.UUID,
        data: MessageCreate
    ) -> Message:
        await MessageService._check_order_participant(session, order_id, sender_id)

        message = Message(
            order_id=order_id,
            sender_id=sender_id,
            **data.model_dump()
        )
        result = await MessageDao.create(session, message)
        return result

    @staticmethod
    async def get_by_order_id(
        session: AsyncSession,
        order_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> list[Message]:
        await MessageService._check_order_participant(session, order_id, user_id)

        result = await MessageDao.get_by_order_id(session, order_id)
        return result

    @staticmethod
    async def _check_order_participant(
            session: AsyncSession,
            order_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> None:
        order = await OrderDao.get_by_id(session, order_id)
        if not order:
            raise NotFoundException("Order not found")

        specialist_user_id = None
        if order.specialist_id:
            specialist = await SpecialistDao.get_by_id(session, order.specialist_id)
            if specialist:
                specialist_user_id = specialist.user_id
        if order.user_id != user_id and specialist_user_id != user_id:
            raise ValidationException(["You are not a participant of this order"])