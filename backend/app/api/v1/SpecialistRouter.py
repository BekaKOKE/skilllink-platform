import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_admin,
    require_specialist,
    require_any, require_client
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.SpecialistSchema import SpecialistCreate, SpecialistUpdate, SpecialistDto
from backend.app.services.AuditService import AuditService
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/specialists",
    tags=["Specialists"]
)

# =========================
# CREATE SPECIALIST
# =========================
@router.post("/", response_model=SpecialistDto)
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

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.SPECIALIST_CREATED,
        detail=f"Specialist profile created {specialist.id}",
        ip_address=request.client.host
    )

    return specialist

# =========================
# GET SPECIALIST BY ID
# =========================
@router.get("/{specialist_id}", response_model=SpecialistDto)
async def get_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    await AuditService.log(
        session=session,
        action=AuditAction.GET_SPECIALIST,
        detail=f"Requested specialist {specialist_id}",
        ip_address=request.client.host
    )

    return specialist


# =========================
# UPDATE SPECIALIST
# =========================
@router.put("/{specialist_id}", response_model=SpecialistDto)
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

    if specialist.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    updated_specialist = await SpecialistService.update(session, specialist, data)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.SPECIALIST_UPDATED,
        detail=f"Updated specialist {specialist_id}",
        ip_address=request.client.host
    )

    return updated_specialist


# =========================
# DEACTIVATE SPECIALIST
# =========================
@router.patch("/{specialist_id}/deactivate", response_model=SpecialistDto)
async def deactivate_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    if specialist.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    result = await SpecialistService.deactivate(session, specialist)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.SPECIALIST_DEACTIVATED,
        detail=f"Deactivated specialist {specialist_id}",
        ip_address=request.client.host
    )

    return result


# =========================
# DELETE SPECIALIST
# =========================
@router.delete("/{specialist_id}")
async def delete_specialist(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):
    specialist = await SpecialistService.get_by_id(session, specialist_id)

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    await SpecialistService.delete(session, specialist)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.SPECIALIST_DELETED,
        detail=f"Deleted specialist {specialist_id}",
        ip_address=request.client.host
    )

    return {"message": "Specialist deleted"}


# =========================
# VERIFY SPECIALIST
# =========================
@router.patch("/{specialist_id}/verify", response_model=SpecialistDto)
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

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.SPECIALIST_VERIFIED,
        detail=f"Verified specialist {specialist_id}",
        ip_address=request.client.host
    )

    return result


# =========================
# FIND SPECIALISTS NEARBY
# =========================
@router.get("/search/nearby", response_model=SpecialistDto)
async def find_specialists_nearby(
    lat: float,
    lon: float,
    k: int = 1,
    job_type: Optional[str] = None,
    max_price: Optional[int] = None,
    request: Request = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):
    specialists = await SpecialistService.find_specialists_nearby(
        session=session,
        lat=lat,
        lon=lon,
        k=k,
        job_type=job_type,
        max_price=max_price
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.SPECIALIST_SEARCH,
        detail=f"Search specialists near {lat},{lon}",
        ip_address=request.client.host if request else None
    )

    return specialists