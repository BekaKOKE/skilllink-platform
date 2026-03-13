import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.address import Address
from backend.app.schemas.AddressSchema import AddressCreate
from backend.app.services.h3Service import H3Service
from backend.app.dao.AddressDao import AddressDao
from backend.app.validation.CreateValidation import CreateValidation

class AddressService:

    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: uuid.UUID,
        data: AddressCreate,
    ) -> Address:
        await CreateValidation.is_valid_address(session, user_id)

        h3_index = H3Service.geo_to_h3(data.lat, data.lon)

        address = Address(
            user_id=user_id,
            **data.model_dump(exclude={"lat", "lon"}),
            h3_index=h3_index
        )

        result = await AddressDao.create(session, address)
        return result

    @staticmethod
    async def get_by_user_id(
            session: AsyncSession,
            user_id: uuid.UUID
    ) -> Optional[Address]:
        result = await AddressDao.get_by_user_id(session, user_id)
        return result

    @staticmethod
    async def get_all(
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> list[Address]:
        result = await AddressDao.get_all(session,limit,offset)
        return result

    @staticmethod
    async def delete(session: AsyncSession, address: Address) -> None:
        await AddressDao.delete(session, address)