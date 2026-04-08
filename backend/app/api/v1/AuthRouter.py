import uuid
from datetime import datetime, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.Redis import redis_client
from backend.app.core.dependencies import get_current_user
from backend.app.db.models.user import User
from backend.app.schemas.UserSchema import UserCreate
from backend.app.schemas.LoginSchema import LoginRequest
from backend.app.services.AuthService import AuthService
from backend.app.services.UserService import UserService
from backend.app.services.a.AuditService import AuditService
from backend.app.db.session import get_session
from backend.app.db.models.enums import LogType, ServiceType
from backend.app.services.a.TokenBlocklistService import TokenBlocklistService
from backend.app.core.Security import decode_token
from backend.app.core.dependencies import bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials
from backend.app.tasks.email_tasks import send_email_confirmation
from backend.app.tasks.email_tasks import send_password_reset
from backend.app.core.Security import decode_token, hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=dict[str, str])
async def register(
    request: Request,
    data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    user = await AuthService.register(session, data)

    confirmation_token = secrets.token_urlsafe(32)

    await redis_client.setex(
        f"confirm:{confirmation_token}",
        86400,
        str(user.id)
    )

    send_email_confirmation.delay(
        user_email=user.email,
        user_name=user.name,
        token=confirmation_token,
    )

    return {
        "message": "User created successfully",
        "user_id": str(user.id)
    }

@router.get("/confirm-email")
async def confirm_email(
    token: str,
    session: AsyncSession = Depends(get_session)
):
    user_id = await redis_client.get(f"confirm:{token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await UserService.get_by_id(session, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await session.commit()

    await redis_client.delete(f"confirm:{token}")

    return {"message": "Email confirmed successfully"}


@router.post("/login", response_model=dict[str, str])
async def login(
    request: Request,
    data: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    token = await AuthService.login(
        session,
        data.email,
        data.password
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/logout", response_model=dict[str, str])
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    jti = payload.get("jti")
    exp = payload.get("exp")

    now = int(datetime.now(tz=timezone.utc).timestamp())
    ttl = exp - now

    # Добавляем в blocklist только если токен ещё не истёк
    await TokenBlocklistService.add(jti, ttl)

    return {"message": "Successfully logged out"}

import secrets
from backend.app.tasks.email_tasks import send_password_reset

# 1. Запрос сброса пароля
@router.post("/forgot-password")
async def forgot_password(
    email: str,
    session: AsyncSession = Depends(get_session)
):
    user = await UserService.get_by_email(session, email)

    # Всегда возвращаем 200 — чтобы не раскрывать существование email
    if not user:
        return {"message": "If that email exists, a reset link has been sent."}

    token = secrets.token_urlsafe(32)

    # Сохраняем токен в Redis на 30 минут
    await redis_client.setex(
        f"reset:{token}",
        1800,
        str(user.id)
    )

    send_password_reset.delay(
        user_email=user.email,
        user_name=user.name,
        token=token,
    )

    return {"message": "If that email exists, a reset link has been sent."}


# 2. Применение нового пароля
@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    session: AsyncSession = Depends(get_session)
):
    user_id = await redis_client.get(f"reset:{token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await UserService.get_by_id(session, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    await session.commit()

    # Удаляем токен чтобы нельзя было использовать повторно
    await redis_client.delete(f"reset:{token}")

    return {"message": "Password reset successfully"}