from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.UserSchema import UserCreate
from backend.app.schemas.LoginSchema import LoginRequest
from backend.app.services.AuthService import AuthService
from backend.app.services.AuditService import AuditService
from backend.app.db.session import get_session
from backend.app.db.models.enums import AuditAction

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