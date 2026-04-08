import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import (
    get_current_user,
    require_any
)
from backend.app.db.models import OrderRequest
from backend.app.db.models.enums import ServiceType, LogType
from backend.app.db.models.user import User
from backend.app.db.session import get_session
from backend.app.schemas.OrderRequestsSchema import OrderRequestCreate
from backend.app.schemas.UserSchema import UserUpdate, UserDto
from backend.app.services.OrderRequestsService import OrderRequestsService
from backend.app.services.UserService import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# GET CURRENT USER
# =========================
@router.get("/profile", response_model=UserDto)
async def get_me(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================
# UPDATE USER
# =========================
@router.put("/update/{user_id}", response_model=UserDto)
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
    if current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update")

    updated_user = await UserService.update(session, user, data)

    return updated_user


# =========================
# DELETE USER
# =========================
@router.delete("/delete/{user_id}", response_model=dict[str, str])
async def delete_user(
    user_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_any)
):
    user = await UserService.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete")

    await UserService.delete(session, user)

    return {"message": "User deleted"}