import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    require_client,
    get_current_user
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.AddressSchema import AddressCreate
from backend.app.services.AddressService import AddressService
from backend.app.services.AuditService import AuditService

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)

# ─────────────────────────────────────────
# CREATE ADDRESS
# ─────────────────────────────────────────

@router.post("/")
async def create_address(
    data: AddressCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    address = await AddressService.create(
        session,
        current_user.id,
        data
    )

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.CREATE_ADDRESS,
        detail=f"Address created {address.id}",
        ip_address=request.client.host
    )

    return address


# ─────────────────────────────────────────
# GET MY ADDRESS
# ─────────────────────────────────────────

@router.get("/me")
async def get_my_address(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    address = await AddressService.get_by_user_id(
        session,
        current_user.id
    )

    if not address:
        raise HTTPException(404, "Address not found")

    return address

# ─────────────────────────────────────────
# DELETE ADDRESS
# ─────────────────────────────────────────

@router.delete("/{address_id}")
async def delete_address(
    address_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_client)
):

    addresses = await AddressService.get_all(session)

    address = next(
        (a for a in addresses if a.id == address_id),
        None
    )

    if not address:
        raise HTTPException(404, "Address not found")

    if address.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Not allowed")

    await AddressService.delete(session, address)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_ADDRESS,
        detail=f"Deleted address {address_id}",
        ip_address=request.client.host
    )

    return {"message": "Address deleted"}