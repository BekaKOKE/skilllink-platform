import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dao.SpecialistDao import SpecialistDao
from backend.app.db.models.specialist import Specialist
from backend.app.schemas.SpecialistSchema import SpecialistCreate, SpecialistUpdate
from backend.app.services.H3zonestatsservice import H3ZoneStatsService
from backend.app.services.h3Service import H3Service
from backend.app.validation.CreateValidation import CreateValidation


class SpecialistService:

    @staticmethod
    async def create(
            session: AsyncSession,
            user_id: uuid.UUID,
            data: SpecialistCreate
    ) -> Specialist:
        await CreateValidation.is_valid_specialist(session, user_id)

        h3_index = H3Service.geo_to_h3(data.lat, data.lon)

        specialist = Specialist(
            user_id=user_id,
            h3_index=h3_index
        )

        result = await SpecialistDao.create(session, specialist)
        await H3ZoneStatsService.on_specialist_created(session, specialist)
        return result

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> list[Specialist]:
        result = await SpecialistDao.get_all(session, limit, offset)
        return result

    @staticmethod
    async def get_by_id(session: AsyncSession, specialist_id: uuid.UUID) -> Optional[Specialist]:
        result = await SpecialistDao.get_by_id(session, specialist_id)
        return result

    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[Specialist]:
        result = await SpecialistDao.get_by_user_id(session, user_id)
        return result

    @staticmethod
    async def get_by_name_surname(session: AsyncSession, name: str, surname: str) -> Optional[Specialist]:
        result = await SpecialistDao.get_by_name_surname(session, name, surname)
        return result

    @staticmethod
    async def update(session: AsyncSession, specialist: Specialist, data: SpecialistUpdate) -> Specialist:
        old_h3 = specialist.h3_index
        update_data = data.model_dump(exclude_none=True)
        result = await SpecialistDao.update(session, specialist, update_data)

        new_h3 = result.h3_index
        if new_h3 and new_h3 != old_h3:
            await H3ZoneStatsService.on_specialist_h3_changed(session, old_h3, new_h3)

        return result

    @staticmethod
    async def deactivate(session: AsyncSession, specialist: Specialist) -> Specialist:
        result = await SpecialistDao.deactivate(session, specialist)
        await H3ZoneStatsService.on_specialist_deactivated(session, result)
        return result

    @staticmethod
    async def delete(session: AsyncSession, specialist: Specialist) -> None:
        h3_index = specialist.h3_index
        await SpecialistDao.delete(session, specialist)
        await H3ZoneStatsService.on_specialist_deleted(session, h3_index)

    @staticmethod
    async def find_specialists_nearby(
            session: AsyncSession,
            lat: float,
            lon: float,
            k: int = 1,
            job_type: Optional[str] = None,
            max_price: Optional[int] = None
    ) -> list[Specialist]:
        center_cell = H3Service.geo_to_h3(lat, lon)
        neighbor_cells = H3Service.get_neighbors(center_cell, k)

        result = await SpecialistDao.find_specialists_nearby(session, neighbor_cells, job_type, max_price)
        return result


    # ─────────────────────────────────────────
    # VERIFY (только admin)
    # ─────────────────────────────────────────

    @staticmethod
    async def verify(session: AsyncSession, specialist: Specialist) -> Specialist:
        result = await SpecialistDao.verify(session, specialist)
        await H3ZoneStatsService.on_specialist_verified(session, result)
        return result