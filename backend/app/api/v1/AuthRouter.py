from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import get_current_user
from backend.app.db.models.user import User
from backend.app.schemas.UserSchema import UserCreate
from backend.app.schemas.LoginSchema import LoginRequest
from backend.app.services.AuthService import AuthService
from backend.app.services.AuditService import AuditService
from backend.app.db.session import get_session
from backend.app.db.models.enums import AuditAction
from backend.app.services.TokenBlocklistService import TokenBlocklistService
from backend.app.core.Security import decode_token
from backend.app.core.dependencies import bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(
    request: Request,
    data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    user = await AuthService.register(session, data)

    await AuditService.log(
        session=session,
        action=AuditAction.USER_REGISTER,
        user_id=user.id,
        detail=f"User registered with email {user.email}",
        ip_address=request.client.host
    )

    return {
        "message": "User created successfully",
        "user_id": str(user.id)
    }


@router.post("/login")
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
        await AuditService.log(
            session=session,
            action=AuditAction.LOGIN_FAILED,
            detail=f"Failed login attempt for {data.email}",
            ip_address=request.client.host
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    await AuditService.log(
        session=session,
        action=AuditAction.LOGIN_SUCCESS,
        detail=f"User {data.email} logged in",
        ip_address=request.client.host
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),  # проверяет подпись и blocklist
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