import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select

from backend.app.db.models.comment import Comment
from backend.app.db.models.enums import OrderStatus
from backend.app.db.models.order import Order
from backend.app.schemas.CommentSchema import CommentFilter


class CommentDao:

    @staticmethod
    async def create(session: AsyncSession, comment: Comment) -> Comment:
        session.add(comment)
        await session.flush()
        return comment

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        specialist_id: uuid.UUID,
        filters: CommentFilter
    ) -> Sequence[Comment]:
        query = (
            select(Comment).where(Comment.specialist_id == specialist_id)
        )
        query = CommentDao.apply_filters(query, filters)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_all(
            session: AsyncSession,
            filters: CommentFilter,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Sequence[Comment]:
        query = (
            select(Comment).order_by(Comment.specialist_id)
        )
        query = CommentDao.apply_filters(query, filters)
        if limit is None:
            limit = 50
        if offset is None:
            offset = 0
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def delete(
        session: AsyncSession,
        comment: Comment
    ) -> None:
        await session.delete(comment)
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

    @staticmethod
    def apply_filters(query: Select, filters: CommentFilter) -> Select:

        if filters.user_id:
            query = query.where(Comment.user_id == filters.user_id)

        if filters.date_from:
            query = query.where(Comment.created_at >= filters.date_from)

        if filters.date_to:
            query = query.where(Comment.created_at <= filters.date_to)

        return query