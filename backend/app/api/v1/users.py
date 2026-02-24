from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID

from backend.app.core.dependencies import get_db, get_current_user, require_role
from backend.app.db.models.user import User
from backend.app.db.models.enums import UserRole
from backend.app.schemas.user import UserResponse
from backend.app.services.audit_service import AuditService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Профиль текущего пользователя."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_role([UserRole.admin, UserRole.regulator])),
):
    """Получить пользователя по ID (только admin/regulator)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def deactivate_user(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Деактивировать пользователя (admin или сам пользователь)."""
    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    AuditService.log_action(
        db=db,
        action="USER_DEACTIVATED",
        request=request,
        user=current_user,
        resource="users",
        resource_id=user_id,
    )

    return {"detail": "User deactivated"}


@router.patch("/{user_id}/activate")
def activate_user(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.admin])),
):
    """Реактивировать деактивированного пользователя (только admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=400, detail="User is already active")

    user.is_active = True
    db.commit()

    AuditService.log_action(
        db=db,
        action="USER_ACTIVATED",
        request=request,
        user=current_user,
        resource="users",
        resource_id=user_id,
    )

    return {"detail": "User activated"}