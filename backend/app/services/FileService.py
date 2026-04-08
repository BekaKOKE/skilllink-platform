import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dao.FileDao import FileDao


class FileService:

    @staticmethod
    async def get_avatar(session: AsyncSession, specialist_id: uuid.UUID):
        result = await FileDao.get_avatar(session, specialist_id)
        return result