import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.models.message import Message

class MessageDao:

    @staticmethod
    async def create(
        session: AsyncSession,
        message: Message,
    ) -> Message:

        session.add(message)
        await session.flush()
        return message

    @staticmethod
    async def get_by_order_id(
        session: AsyncSession,
        order_id: uuid.UUID
    ) -> Sequence[Message]:

        result = await session.execute(
            select(Message)
            .where(Message.order_id == order_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()