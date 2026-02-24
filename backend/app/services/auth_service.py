from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.db.models.user import User
from backend.app.core.security import hash_password, verify_password, create_access_token


class AuthService:

    @staticmethod
    def register(db: Session, data):
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            email=data.email,
            role=data.role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()

        if not user or not verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        token = create_access_token({"sub": str(user.id)})
        return token