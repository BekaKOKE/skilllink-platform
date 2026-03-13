import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_client
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.RateSchema import RateCreate
from backend.app.services.AuditService import AuditService
from backend.app.services.RateService import RateService

router = APIRouter(
    prefix="/rates",
    tags=["Rates"]
)

# ─────────────────────────────────────────
# CREATE RATE
# ─────────────────────────────────────────

@router.post("/")
async def create_rate(
    data: RateCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    rate = await RateService.create(
        session,
        current_user.id,
        data
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_RATE,
        detail=f"Rate created {rate.id}",
        ip_address=request.client.host
    )

    return rate


# ─────────────────────────────────────────
# GET SPECIALIST RATES
# ─────────────────────────────────────────

@router.get("/specialist/{specialist_id}")
async def get_specialist_rates(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
):

    rates = await RateService.get_specialist_rates(
        session,
        specialist_id
    )

    await AuditService.log(
        session=session,
        action=AuditAction.GET_SPECIALIST_RATES,
        detail=f"Requested rates for specialist {specialist_id}",
        ip_address=request.client.host
    )

    return rates


# ─────────────────────────────────────────
# GET USER RATE FOR SPECIALIST
# ─────────────────────────────────────────

@router.get("/specialist/{specialist_id}/me")
async def get_my_rate(
    specialist_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    rate = await RateService.get_user_rate(
        session,
        current_user.id,
        specialist_id
    )

    return rate


# ─────────────────────────────────────────
# DELETE RATE
# ─────────────────────────────────────────

@router.delete("/{rate_id}")
async def delete_rate(
    rate_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    rates = await RateService.get_specialist_rates(session, current_user.id)
    rate = next((r for r in rates if r.id == rate_id), None)

    if not rate:
        raise HTTPException(404, "Rate not found")

    if rate.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    await RateService.delete(session, rate)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_RATE,
        detail=f"Deleted rate {rate_id}",
        ip_address=request.client.host
    )

    return {"message": "Rate deleted"}