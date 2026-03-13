import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dao.AddressDao import AddressDao
from backend.app.dao.CatalogDao import CatalogDao
from backend.app.dao.UserDao import UserDao
from backend.app.dao.SpecialistDao import SpecialistDao
from backend.app.dao.RateDao import RateDao
from backend.app.dao.CommentDao import CommentDao
from backend.app.schemas.CatalogSchema import CatalogCreate, CatalogFilter
from backend.app.schemas.CommentSchema import CommentCreate, CommentFilter
from backend.app.schemas.RateSchema import RateCreate
from backend.app.schemas.UserSchema import UserCreate
from backend.app.exceptions.ValidationException import ValidationException

class CreateValidation:

    @staticmethod
    async def is_valid_user(session: AsyncSession, data: UserCreate) -> None:
        errors = []

        if await UserDao.get_by_email(session, data.email):
            errors.append(f"User with this email already exists")

        if await UserDao.get_by_phone(session, data.phone):
            errors.append(f"User with this phone already exists")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    async def is_valid_specialist(session: AsyncSession, user_id: uuid.UUID) -> None:
        errors = []

        if await SpecialistDao.get_by_user_id(session, user_id):
            errors.append("Specialist profile already exists for this user")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    async def is_valid_catalog(session: AsyncSession, specialist_id: uuid.UUID, data: CatalogCreate) -> None:
        errors = []
        filters = CatalogFilter(
            job_type=data.job_type
        )
        if await CatalogDao.get_by_specialist_id(session, specialist_id, filters):
            errors.append("Specialist catalog already exists for this job type")
        specialist = await SpecialistDao.get_by_id(session, specialist_id)
        if specialist is None:
            errors.append("Specialist not found")
        elif not specialist.is_verified:
            errors.append("Specialist is not verified to create this catalog")
        if errors:
            raise ValidationException(errors)

    @staticmethod
    async def is_valid_address(session: AsyncSession, user_id: uuid.UUID) -> None:
        errors = []

        if await AddressDao.get_by_user_id(session, user_id):
            errors.append("Address profile already exists for this user")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    async def is_valid_rate(
            session: AsyncSession,
            user_id: uuid.UUID,
            data: RateCreate,
            has_order: bool
    ) -> None:
        errors = []

        if not has_order:
            errors.append("You can only rate a specialist after a completed order")

        if await RateDao.get_user_rate(session, user_id, data.specialist_id):
            errors.append("You have already rated this specialist")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    async def is_valid_comment(
            session: AsyncSession,
            user_id: uuid.UUID,
            data: CommentCreate,
            has_order: bool
    ) -> None:
        errors = []
        filters = CommentFilter(
            user_id = user_id
        )
        if not has_order:
            errors.append("You can only comment a specialist after a completed order")

        if await CommentDao.get_by_id(session, data.specialist_id, filters):
            errors.append("You have already commented this specialist")

        if errors:
            raise ValidationException(errors)