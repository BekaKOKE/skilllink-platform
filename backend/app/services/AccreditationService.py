import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.accreditation import Accreditation
from backend.app.schemas.AccreditationSchema import AccreditationCreate
from backend.app.dao.AccreditationDao import AccreditationDao

class AccreditationService:

    @staticmethod
    async def create(
        session: AsyncSession,
        specialist_id: uuid.UUID,
        data: AccreditationCreate
    ) -> Accreditation:
        accreditation = Accreditation(
            specialist_id=specialist_id,
            **data.model_dump()
        )
        result = await AccreditationDao.create(session, accreditation)
        return result

    @staticmethod
    async def delete(
            session: AsyncSession,
            accreditation: Accreditation
    ) -> None:
        await AccreditationDao.delete(session, accreditation)

    @staticmethod
    async def get_by_specialist_id(
        session: AsyncSession,
        specialist_id: uuid.UUID
    ) -> list[Accreditation]:
        result = await AccreditationDao.get_by_specialist_id(session, specialist_id)
        return result

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    )-> list[Accreditation]:
        result = await AccreditationDao.get_all(session, limit, offset)
        return result