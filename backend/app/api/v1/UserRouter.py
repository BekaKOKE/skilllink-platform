import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    get_current_user,
    require_any
)
from backend.app.db.models.enums import AuditAction
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.UserSchema import UserUpdate, UserDto
from backend.app.services.AuditService import AuditService
from backend.app.services.UserService import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# GET CURRENT USER
# =========================
@router.get("/me/profile", response_model=UserDto)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================
# UPDATE USER
# =========================
@router.put("/{user_id}", response_model=UserDto)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):
    user = await UserService.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # пользователь может менять только себя
    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    updated_user = await UserService.update(session, user, data)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.UPDATE_USER,
        detail=f"User {current_user.id} updated user {user_id}",
        ip_address=request.client.host
    )

    return updated_user


# =========================
# DELETE USER
# =========================
@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):
    user = await UserService.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await UserService.delete(session, user)

    await AuditService.log(
        session=session,
        user_id=current_user.id,
        action=AuditAction.DELETE_USER,
        detail=f"Admin {current_user.id} deleted user {user_id}",
        ip_address=request.client.host
    )

    return {"message": "User deleted"}