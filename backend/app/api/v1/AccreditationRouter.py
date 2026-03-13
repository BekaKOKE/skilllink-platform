import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_specialist
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.AccreditationSchema import AccreditationCreate, AccreditationDto
from backend.app.services.AccreditationService import AccreditationService
from backend.app.services.AuditService import AuditService
from backend.app.services.SpecialistService import SpecialistService

router = APIRouter(
    prefix="/accreditations",
    tags=["Accreditations"]
)

# ─────────────────────────────────────────
# CREATE ACCREDITATION
# ─────────────────────────────────────────

@router.post("/", response_model=AccreditationDto)
async def create_accreditation(
    data: AccreditationCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if not specialist:
        raise HTTPException(404, "Specialist profile not found")

    accreditation = await AccreditationService.create(
        session,
        specialist.id,
        data
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_ACCREDITATION,
        detail=f"Accreditation created {accreditation.id}",
        ip_address=request.client.host
    )

    return accreditation


# ─────────────────────────────────────────
# GET SPECIALIST ACCREDITATIONS
# ─────────────────────────────────────────

@router.get("/specialist/{specialist_id}", response_model=AccreditationDto)
async def get_specialist_accreditations(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session)
):

    result = await AccreditationService.get_by_specialist_id(
        session,
        specialist_id
    )

    await AuditService.log(
        session=session,
        action=AuditAction.GET_SPECIALIST_ACCREDITATIONS,
        detail=f"Requested accreditations of specialist {specialist_id}",
        ip_address=request.client.host
    )

    return result

# ─────────────────────────────────────────
# DELETE ACCREDITATION
# ─────────────────────────────────────────

@router.delete("/{accreditation_id}")
async def delete_accreditation(
    accreditation_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_specialist)
):

    items = await AccreditationService.get_all(session)

    accreditation = next(
        (i for i in items if i.id == accreditation_id),
        None
    )

    if not accreditation:
        raise HTTPException(404, "Accreditation not found")

    specialist = await SpecialistService.get_by_user_id(session, current_user.id)

    if accreditation.specialist_id != specialist.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    await AccreditationService.delete(session, accreditation)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_ACCREDITATION,
        detail=f"Deleted accreditation {accreditation_id}",
        ip_address=request.client.host
    )

    return {"message": "Accreditation deleted"}