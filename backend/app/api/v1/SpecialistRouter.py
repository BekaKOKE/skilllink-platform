import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_admin,
    require_specialist,
    require_client, get_current_user
)
import base64
from fastapi import UploadFile, File
from backend.app.tasks.image_tasks import compress_and_store_image
from backend.app.core.config import settings
from backend.app.db.models.enums import ServiceType,LogType
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.SpecialistSchema import SpecialistCreate, SpecialistUpdate, SpecialistDto
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/specialists",
    tags=["Specialists"]
)

# =========================
# CREATE SPECIALIST
# =========================
@router.post("/create", response_model=SpecialistDto)
async def create_specialist(
    request: Request,
    data: SpecialistCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):
    specialist = await SpecialistService.create(
        session=session,
        user_id=current_user.id,
        data=data
    )

    return specialist

# =========================
# GET SPECIALIST BY ID
# =========================
@router.get("/get/{specialist_id}", response_model=SpecialistDto)
async def get_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    return specialist


# =========================
# UPDATE SPECIALIST
# =========================
@router.put("/update/{specialist_id}", response_model=SpecialistDto)
async def update_specialist(
    specialist_id: uuid.UUID,
    data: SpecialistUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    if specialist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update")

    updated_specialist = await SpecialistService.update(session, specialist, data)

    return updated_specialist


# =========================
# DEACTIVATE SPECIALIST
# =========================
@router.patch("/deactivate/{specialist_id}", response_model=SpecialistDto)
async def deactivate_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    if specialist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to deactivate")

    result = await SpecialistService.deactivate(session, specialist)

    return result


# =========================
# DELETE SPECIALIST
# =========================
@router.delete("/delete/{specialist_id}", response_model=dict[str, str])
async def delete_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    if specialist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete")

    await SpecialistService.delete(session, specialist)

    return {"message": "Specialist deleted"}


# =========================
# VERIFY SPECIALIST
# =========================
@router.patch("/verify/{specialist_id}", response_model=SpecialistDto)
async def verify_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    result = await SpecialistService.verify(session, specialist)

    return result


# =========================
# FIND SPECIALISTS NEARBY
# =========================
@router.get("/search", response_model=list[SpecialistDto])
async def find_specialists_nearby(
    lat: float,
    lon: float,
    k: int = 1,
    job_type: Optional[str] = None,
    max_price: Optional[int] = None,
    request: Request = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):
    specialists = await SpecialistService.find_specialists_nearby(
        session=session,
        lat=lat,
        lon=lon,
        k=k,
        job_type=job_type,
        max_price=max_price
    )

    return specialists