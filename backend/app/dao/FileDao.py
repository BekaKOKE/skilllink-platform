import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class FileDao:
    @staticmethod
    async def get_avatar(session: AsyncSession, specialist_id: uuid.UUID):
        result = await session.execute(
            text("""
                SELECT image_data, content_type
                FROM specialist_images
                WHERE specialist_id = :specialist_id
                ORDER BY uploaded_at DESC
                LIMIT 1
            """),
            {"specialist_id": str(specialist_id)}
        )
        return result.first()