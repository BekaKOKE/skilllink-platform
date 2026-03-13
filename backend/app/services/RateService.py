import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.rate import Rate
from backend.app.schemas.RateSchema import RateCreate
from backend.app.dao.RateDao import RateDao
from backend.app.validation.CreateValidation import CreateValidation

class RateService:

    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: uuid.UUID,
        data: RateCreate
    ) -> Rate:
        has_order = await RateDao.check_completed_order(
            session, user_id, data.specialist_id
        )
        await CreateValidation.is_valid_rate(session, user_id, data, has_order)

        rate = Rate(user_id=user_id, **data.model_dump())
        result = await RateDao.create(session, rate)
        return result

    @staticmethod
    async def delete(session: AsyncSession, rate: Rate) -> None:
        await RateDao.delete(session, rate)

    @staticmethod
    async def get_specialist_rates(
        session: AsyncSession,
        specialist_id: uuid.UUID
    ) -> list[Rate]:
        result = await RateDao.get_specialist_rates(session, specialist_id)
        return result

    @staticmethod
    async def get_user_rate(
            session: AsyncSession,
            user_id: uuid.UUID,
            specialist_id: uuid.UUID
    ) -> Rate:
        result = await RateDao.get_user_rate(session, user_id, specialist_id)
        return result