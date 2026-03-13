import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.comment import Comment
from backend.app.schemas.CommentSchema import CommentCreate, CommentFilter
from backend.app.dao.CommentDao import CommentDao
from backend.app.validation.CreateValidation import CreateValidation

class CommentService:

    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: uuid.UUID,
        data: CommentCreate
    ) -> Comment:
        has_order = await CommentDao.check_completed_order(
            session, user_id, data.specialist_id
        )
        await CreateValidation.is_valid_comment(session, user_id, data, has_order)

        comment = Comment(user_id=user_id, **data.model_dump())
        result = await CommentDao.create(session, comment)
        return result

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        specialist_id: uuid.UUID,
        filters: CommentFilter
    ) -> list[Comment]:
        result = await CommentDao.get_by_id(session, specialist_id, filters)
        return result

    @staticmethod
    async def get_all(
            session: AsyncSession,
            filters: CommentFilter,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> list[Comment]:
        result = await CommentDao.get_all(session, filters,limit,offset)
        return result

    @staticmethod
    async def delete(session: AsyncSession, comment: Comment) -> None:
        await CommentDao.delete(session, comment)