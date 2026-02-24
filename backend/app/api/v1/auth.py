from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.db.models.user import User
from backend.app.services.audit_service import AuditService
from backend.app.schemas.user import UserCreate, UserLogin
from backend.app.services.auth_service import AuthService
from backend.app.core.dependencies import get_db

router = APIRouter()


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register(db, data)


@router.post("/login")
def login(
    data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    token = AuthService.login(db, data.username, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = db.query(User).filter(User.username == data.username).first()

    AuditService.log_action(
        db=db,
        action="USER_LOGIN",
        request=request,
        user=user,
        resource="auth"
    )

    return {"access_token": token, "token_type": "bearer"}